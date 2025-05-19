import datetime

import psycopg
import sqlalchemy
from sqlalchemy import CursorResult, select, func, Select

from src.core.interfaces import BaseSQLRepository
from src.core.schemas import borrowed_books, books, readers
from src.core.types import ID, IDModel
from src.services.books.exc import BookNotFound
from src.services.borrowed_books.dto.input import INPUT_CreateBorrowedBook, INPUT_ReturnBook
from src.services.borrowed_books.exc import BorrowedLimitExceeded, ReaderAlreadyHasBook, BorrowNotFound, \
    AllBooksBorrowed
from src.services.readers.exc import ReaderNotFound


class DB_GiveOutBook(BaseSQLRepository):
    """ Класс отвечает за операцию выдачи книги читателю """

    def _status(self, reader_id: ID, book_id: ID):
        """ Проверяет есть ли свободные экземпляры книги в наличии у библиотеки,
        и есть ли экземпляры этой же книги на руках у читателя (нужно для разных ошибок) и возвращает результат.
        Читатель не может взять одну и ту же книгу больше чем в 1 экземпляре"""
        check_book = (
            select(books.c.quantity)
            .where(books.c.id == book_id)
            .scalar_subquery()
        )  # проверка наличия экземпляра у библиотеки

        borrowed_books_list = (
            select(
                func.coalesce(
                    func.json_agg(
                        func.json_build_object(
                            "borrowed_id", borrowed_books.c.id,
                            "borrowed_book_id", borrowed_books.c.book_id
                        ).label("borrowed_books")
                    ),
                    func.json_build_array()
                ).label("borrowed_books")
            )
            .where(borrowed_books.c.reader_id == reader_id)
            .where(borrowed_books.c.return_date.is_(None))
            .cte("borrowed_books_list")
        )  # проверка наличия книги на руках у читателя

        return (
            select(
                check_book.label("needed_book_quantity"),
                borrowed_books_list
            )
        )

    def _save_borrowed_book_stmt(self, reader_id: ID, book_id: ID):
        """ Уменьшает доступные экземпляры на 1 и отдает книгу читателю, записывая ее ему в долги"""
        book_cte = (
            books
            .update()
            .values(quantity=books.c.quantity - 1)
            .where(books.c.id == book_id)
            .returning(books.c.id)
            .cte("book_cte")
        )  # уменьшаем в библиотеке

        return (
            borrowed_books
            .insert()
            .values(reader_id=reader_id, book_id=select(book_cte.c.id).scalar_subquery())
            .returning(borrowed_books.c.id)
        )  # увеличиваем долг читателя

    async def __call__(self, model: INPUT_CreateBorrowedBook):
        async with self.engine.connect() as connection:
            cursor: CursorResult = await connection.execute(self._status(model.reader_id, model.book_id))
            status = cursor.mappings().fetchone()
            if status["needed_book_quantity"] is None:  # Если книги нет вообще
                raise BookNotFound(model.book_id)
            if status["needed_book_quantity"] == 0:  # Если все экземпляры книги на руках
                raise AllBooksBorrowed(model.book_id)
            if len(status["borrowed_books"]) == 3:  # Если читатель уже торчит 3 книги
                raise BorrowedLimitExceeded(model.reader_id)
            if model.book_id in [
                borrowed_book["borrowed_book_id"]
                for borrowed_book
                in status["borrowed_books"]
            ]:  # Если эта книга уже у читателя есть
                raise ReaderAlreadyHasBook(model.reader_id, model.book_id)
            try:
                cursor = await connection.execute(self._save_borrowed_book_stmt(model.reader_id, model.book_id))
                await connection.commit()
                return IDModel(id=cursor.scalar())
            except sqlalchemy.exc.IntegrityError as e:
                if isinstance(e.orig, psycopg.errors.ForeignKeyViolation):  # Если читатель не найден
                    raise ReaderNotFound(model.reader_id)


class DB_ReturnBook(BaseSQLRepository):
    """ Класс отвечает за операцию возврата книги в библиотеку """

    def _status(self, reader_id: ID, book_id: ID):
        """ Проверяет есть ли данная книга на руках у читателя """

        return (
            select(borrowed_books.c.id)
            .where(borrowed_books.c.book_id == book_id)
            .where(borrowed_books.c.reader_id == reader_id)
            .where(borrowed_books.c.return_date.is_(None))
        )

    def _stmt(self, borrow_id: ID):
        """ Возвращает книгу обратно в библиотеку """
        add_return_date = (
            borrowed_books
            .update()
            .values(return_date=datetime.datetime.now())
            .where(borrowed_books.c.id == borrow_id)
            .returning(borrowed_books.c.book_id)
            .cte("add_return_date")
        )  # фиксируем когда читатель отдал книгу

        return (
            books
            .update()
            .values(quantity=books.c.quantity + 1)
            .where(books.c.id == select(add_return_date.c.book_id).scalar_subquery())
        )  # прибавляем экземпляр в библиотеке

    async def __call__(self, model: INPUT_ReturnBook):
        async with self.engine.connect() as connection:
            cursor: CursorResult = await connection.execute(self._status(model.reader_id, model.book_id))
            borrow_id = cursor.scalar()
            if borrow_id is None:  # если такой задолженности нет (либо читателя не существует)
                raise BorrowNotFound(model.reader_id, model.book_id)
            await connection.execute(self._stmt(borrow_id))
            await connection.commit()


class DB_GetBorrowList(BaseSQLRepository):
    async def __call__(self, skip: int, limit: int, no_returned_only: bool):
        async with self.engine.connect() as connection:
            cursor: CursorResult = await connection.execute(self._stmt(skip, limit, no_returned_only))
            return cursor.mappings().fetchall()

    def _stmt(self, skip: int, limit: int, no_returned_only: bool):
        stmt: Select = (
            select(
                borrowed_books.c.id,
                func.json_build_object(
                    "id", readers.c.id,
                    "name", readers.c.name,
                    "email", readers.c.email
                ).label("reader"),
                func.coalesce(
                    func.json_agg(
                        func.json_build_object(
                            "id", books.c.id,
                            "title", books.c.title,
                            "author", books.c.author,
                            "isbn", books.c.isbn,
                            "year", books.c.year
                        )
                    ),
                    func.json_build_array()
                ).label("borrowed_books"),
                borrowed_books.c.borrow_date,
                borrowed_books.c.return_date
            )
            .join(readers, borrowed_books.c.reader_id == readers.c.id)
            .join(books, borrowed_books.c.book_id == books.c.id)
        )
        if no_returned_only:
            stmt = stmt.where(borrowed_books.c.return_date.is_(None))
        stmt = stmt.offset(skip).limit(limit)
        stmt = stmt.group_by(
            borrowed_books.c.id,
            readers.c.id,
            borrowed_books.c.borrow_date,
            borrowed_books.c.return_date
        )
        return stmt
