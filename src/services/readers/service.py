from fastapi import Depends
from loguru import logger

from src.core.interfaces import BaseService
from src.core.types import ID
from src.services.readers.dto.input import INPUT_CreateReader, INPUT_UpdateReader
from src.services.readers.repository import (
    DB_CreateReader,
    DB_GetReaderById,
    DB_GetReaderList,
    DB_UpdateReader,
    DB_DeleteReader
)


class SERVICE_CreateReader(BaseService):
    def __init__(
            self,
            repository: DB_CreateReader = Depends()
    ):
        super().__init__()
        self._repository = repository

    async def __call__(self, client_id: ID, model: INPUT_CreateReader):
        result = await self._repository(model)
        logger.info(f"Библиотекарь с ID {client_id} добавил читателя с ID {result.id}")
        return result


class SERVICE_UpdateReader(BaseService):
    def __init__(
            self,
            repository: DB_UpdateReader = Depends()
    ):
        super().__init__()
        self._repository = repository

    async def __call__(self, client_id: ID, reader_id: ID, model: INPUT_UpdateReader):
        result = await self._repository(reader_id, model)
        logger.info(f"Библиотекарь с ID {client_id} обновил данные читателя с ID {result.id}")
        return result


class SERVICE_GetReaderById(BaseService):
    def __init__(
            self,
            repository: DB_GetReaderById = Depends()
    ):
        super().__init__()
        self._repository = repository

    async def __call__(self, reader_id: ID):
        return await self._repository(reader_id)


class SERVICE_GetReaderList(BaseService):
    def __init__(
            self,
            repository: DB_GetReaderList = Depends()
    ):
        super().__init__()
        self._repository = repository

    async def __call__(self, borrowings, skip: int, limit: int):
        return await self._repository(borrowings, skip, limit)


class SERVICE_DeleteReader(BaseService):
    def __init__(
            self,
            repository: DB_DeleteReader = Depends()
    ):
        super().__init__()
        self._repository = repository

    async def __call__(self, client_ID: ID, reader_id: ID):
        await self._repository(reader_id)
        logger.info(f"Библиотекарь с ID {client_ID} удалил читателя с ID {reader_id}")
