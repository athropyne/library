import psycopg
import sqlalchemy
from sqlalchemy import CursorResult

from src.core.interfaces import BaseSQLRepository
from src.core.schemas import librarians
from src.core.types import IDModel
from src.services.librarians.dto.input import INPUT_CreateLibrarian
from src.services.librarians.exc import LibrarianAlreadyExists


class DB_CreateLibrarian(BaseSQLRepository):
    def _stmt(self, model: INPUT_CreateLibrarian):
        return (
            librarians
            .insert()
            .values(**model.model_dump())
            .returning(librarians.c.id)
        )

    async def __call__(self, model: INPUT_CreateLibrarian):
        async with self.engine.connect() as connection:
            try:
                cursor: CursorResult = await connection.execute(self._stmt(model))
                await connection.commit()
                return IDModel(id=cursor.scalar())
            except sqlalchemy.exc.IntegrityError as e:
                await connection.rollback()
                if isinstance(e.orig, psycopg.errors.UniqueViolation):
                    raise LibrarianAlreadyExists(model.login)

