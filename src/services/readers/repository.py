import psycopg
import sqlalchemy
from sqlalchemy import CursorResult, select, exists, and_, func

from src.core.exc import NoDataToUpdate
from src.core.interfaces import BaseSQLRepository
from src.core.schemas import readers, borrowed_books
from src.core.types import IDModel, ID
from src.services.books.dto.input import HasBorrowings
from src.services.readers.dto.input import INPUT_CreateReader, INPUT_UpdateReader
from src.services.readers.dto.output import OUTPUT_ReaderShortInfo
from src.services.readers.exc import ReaderAlreadyExists, ReaderNotFound, ReaderHasDebts


class DB_CreateReader(BaseSQLRepository):
    def _stmt(self, model: INPUT_CreateReader):
        return (
            readers
            .insert()
            .values(**model.model_dump())
            .returning(readers.c.id)
        )

    async def __call__(self, model: INPUT_CreateReader):
        async with self.engine.connect() as connection:
            try:
                cursor: CursorResult = await connection.execute(self._stmt(model))
                await connection.commit()
                return IDModel(id=cursor.scalar())
            except sqlalchemy.exc.IntegrityError as e:
                if isinstance(e.orig, psycopg.errors.UniqueViolation):
                    raise ReaderAlreadyExists(model.email)


class DB_UpdateReader(BaseSQLRepository):
    def _stmt(self, reader_id: ID, model: INPUT_UpdateReader):
        data = model.model_dump(exclude_none=True)
        if len(data) == 0:
            raise NoDataToUpdate
        return (
            readers
            .update()
            .values(**data)
            .where(readers.c.id == reader_id)
            .returning(readers.c.id)
        )

    async def __call__(self, reader_id: ID, model: INPUT_UpdateReader):
        async with self.engine.connect() as connection:
            try:
                cursor: CursorResult = await connection.execute(self._stmt(reader_id, model))
                if cursor.rowcount != 0:
                    raise ReaderNotFound(reader_id)
                await connection.commit()
                return IDModel(id=reader_id)
            except sqlalchemy.exc.IntegrityError as e:
                if isinstance(e.orig, psycopg.errors.UniqueViolation):
                    raise ReaderAlreadyExists(model.email)


class DB_GetReaderById(BaseSQLRepository):
    def _stmt(self, reader_id: ID):
        return (
            select(
                readers,
                func.coalesce(
                    select(
                        func.json_agg(
                            func.json_build_object(
                                "id", borrowed_books.c.id,
                                "book_id", borrowed_books.c.book_id,
                                "borrow_date", borrowed_books.c.borrow_date
                            )
                        )
                    )
                    .where(borrowed_books.c.reader_id == readers.c.id)
                    .scalar_subquery(),
                    func.json_build_array()
                ).label("borrowings")
            )
            .where(readers.c.id == reader_id)
        )

    async def __call__(self, reader_id: ID):
        async with self.engine.connect() as connection:
            cursor: CursorResult = await connection.execute(self._stmt(reader_id))
        result = cursor.mappings().fetchone()
        if result is None:
            raise ReaderNotFound(reader_id)
        return result
        # return OUTPUT_ReaderFullInfo(**result)


class DB_GetReaderList(BaseSQLRepository):
    def _stmt(self, borrowings: HasBorrowings | None, skip: int, limit: int):
        stmt = (
            select(
                readers.c.id,
                readers.c.name,
                readers.c.email
            )
        )
        match borrowings:
            case HasBorrowings.only_with:
                stmt = stmt.join(borrowed_books, borrowed_books.c.reader_id == readers.c.id)
                stmt = stmt.where(borrowed_books.c.return_date.is_(None))
            case HasBorrowings.only_without:
                stmt = stmt.where(
                    ~exists().where(
                        and_(
                            borrowed_books.c.reader_id == readers.c.id,
                            borrowed_books.c.return_date.is_(None)
                        )
                    )
                )
        stmt = (
            stmt
            .offset(skip)
            .limit(limit)
        )
        return stmt

    async def __call__(self, borrowings: HasBorrowings | None, skip: int, limit: int):
        async with self.engine.connect() as connection:
            cursor: CursorResult = await connection.execute(self._stmt(borrowings, skip, limit))
        result = cursor.mappings().fetchall()
        result = [OUTPUT_ReaderShortInfo(**reader) for reader in result]
        return result


class DB_DeleteReader(BaseSQLRepository):
    def _status(self, reader_id: ID):
        return (
            select(borrowed_books.c.id)
            .where(borrowed_books.c.reader_id == reader_id)
            .where(borrowed_books.c.return_date.is_(None))
        )

    def _stmt(self, reader_id: ID):
        return (
            readers
            .delete()
            .where(readers.c.id == reader_id)
        )

    async def __call__(self, reader_id: ID):
        async with self.engine.connect() as connection:
            cursor: CursorResult = await connection.execute(self._status(reader_id))
            borrowed = cursor.mappings().fetchall()
            if len(borrowed) != 0:
                raise ReaderHasDebts(reader_id)
            cursor = await connection.execute(self._stmt(reader_id))
            if cursor.rowcount != 1:
                raise ReaderNotFound(reader_id)
            await connection.commit()
