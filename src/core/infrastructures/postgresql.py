from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from src.core.config import settings


class Database:
    def __init__(self):
        self.__user = settings.POSTGRES_USER
        self.__password = settings.POSTGRES_PASSWORD
        self.__socket = settings.DB_SOCKET
        self.__dbname = settings.POSTGRES_DB
        self.engine = create_async_engine(
            f"postgresql+psycopg://{self.__user}:{self.__password}@{self.__socket}/{self.__dbname}",
            echo=True if settings.DB_LOGS else False)

    async def init(self, metadata: MetaData):
        async with self.engine.connect() as connection:
            await connection.run_sync(metadata.drop_all)
            await connection.run_sync(metadata.create_all)
            await connection.commit()
        await self.engine.dispose()

    async def dispose(self):
        await self.engine.dispose()

    def __call__(self) -> AsyncEngine:
        return self.engine
