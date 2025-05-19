import psycopg
import sqlalchemy
from sqlalchemy import CursorResult, select
from sqlalchemy.sql.functions import count

from src.core.exc import NoDataToUpdate
from src.core.interfaces import BaseSQLRepository
from src.core.types import IDModel, ID
from src.core.schemas import borrowed_books
from src.services.books.dto.input import INPUT_CreateBook, INPUT_UpdateBook
from src.services.books.dto.output import OUTPUT_BookFullInfo, OUTPUT_BookShortInfo
from src.services.books.exc import ISBNAlreadyExists, BookNotFound
from src.core.schemas import books
from src.services.borrowed_books.exc import ThereAreBorrowings


class DB_CreateBook(BaseSQLRepository):
    def _stmt(self, model: INPUT_CreateBook):
        return (
            books
            .insert()
            .values(**model.model_dump())
            .returning(books.c.id)
        )

    async def __call__(self, model: INPUT_CreateBook):
        async with self.engine.connect() as connection:
            try:
                cursor: CursorResult = await connection.execute(self._stmt(model))
            except sqlalchemy.exc.IntegrityError as e:
                if isinstance(e.orig, psycopg.errors.UniqueViolation):
                    raise ISBNAlreadyExists(model.isbn)
            await connection.commit()
        return IDModel(id=cursor.scalar())


class DB_UpdateBook(BaseSQLRepository):
    def _stmt(self, book_id: ID, model: INPUT_UpdateBook):
        data = model.model_dump(exclude_none=True)
        if len(data) == 0:
            raise NoDataToUpdate
        return (
            books
            .update()
            .values(**model.model_dump())
            .where(books.c.id == book_id)
            .returning(books.c.id)
        )

    async def __call__(self, book_id: ID, model: INPUT_UpdateBook):
        async with self.engine.connect() as connection:
            try:
                cursor: CursorResult = await connection.execute(self._stmt(book_id, model))
                if cursor.rowcount != 1:
                    raise BookNotFound(book_id)
                await connection.commit()
                return IDModel(id=cursor.scalar())
            except sqlalchemy.exc.IntegrityError as e:
                if isinstance(e.orig, psycopg.errors.UniqueViolation) \
                        or isinstance(e.orig, psycopg.errors.NotNullViolation):
                    raise ISBNAlreadyExists(model.isbn)


class DB_GetBookById(BaseSQLRepository):
    def _stmt(self, book_id: ID):
        return (
            select(books)
            .where(books.c.id == book_id)
        )

    async def __call__(self, book_id: ID):
        async with self.engine.connect() as connection:
            cursor: CursorResult = await connection.execute(self._stmt(book_id))
        result = cursor.mappings().fetchone()
        if result is None:
            raise BookNotFound(book_id)
        return OUTPUT_BookFullInfo(**result)


class DB_GetBookList(BaseSQLRepository):
    def _stmt(self, skip: int, limit: int):
        return (
            select(
                books.c.id,
                books.c.title,
                books.c.author,
                books.c.year,
                (books.c.quantity > 0).label("is_available")
            )
            .order_by(books.c.title)
            .offset(skip)
            .limit(limit)
        )

    async def __call__(self, skip: int, limit: int):
        async with self.engine.connect() as connection:
            cursor: CursorResult = await connection.execute(self._stmt(skip, limit))
        result = [OUTPUT_BookShortInfo(**book) for book in cursor.mappings().fetchall()]
        return result


class DB_DeleteBook(BaseSQLRepository):
    def _status(self, book_id: ID):
        return (
            select(count())
            .where(borrowed_books.c.book_id == book_id)
            .where(borrowed_books.c.return_date.is_(None))
        )

    def _stmt(self, book_id: ID):
        return (
            books
            .delete()
            .where(books.c.id == book_id)
        )

    async def __call__(self, book_id: ID):
        async with self.engine.connect() as connection:
            cursor: CursorResult = await connection.execute(self._status(book_id))
            borrowed_books_count = cursor.scalar()
            if borrowed_books_count != 0:
                raise ThereAreBorrowings(book_id)
            cursor = await connection.execute(self._stmt(book_id))
            if cursor.rowcount != 1:
                raise BookNotFound(book_id)
            await connection.commit()
