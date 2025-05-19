from sqlalchemy import CursorResult, select

from src.core.interfaces import BaseSQLRepository
from src.core.schemas import librarians
from src.services.security.exc import InvalidLoginOrPassword


class SQL_DB_GetUserByLogin(BaseSQLRepository):
    async def __call__(self, login: str):
        stmt = select(librarians.c.id, librarians.c.password).where(librarians.c.login == login)
        async with self.engine.connect() as connection:
            cursor: CursorResult = await connection.execute(stmt)
        result = cursor.mappings().fetchone()
        if not result:
            raise InvalidLoginOrPassword
        return result
