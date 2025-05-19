from fastapi import Depends
from loguru import logger

from src.core.interfaces import BaseService
from src.core.types import ID
from src.services.books.dto.input import INPUT_CreateBook, INPUT_UpdateBook
from src.services.books.repository import DB_CreateBook, DB_UpdateBook, DB_GetBookById, DB_GetBookList, DB_DeleteBook


class SERVICE_CreateBook(BaseService):
    def __init__(
            self,
            create_book_repository: DB_CreateBook = Depends()
    ):
        super().__init__()
        self._create_book_repository = create_book_repository

    async def __call__(
            self,
            client_id: ID,
            model: INPUT_CreateBook
    ):
        result = await self._create_book_repository(model)
        logger.info(f"Библиотекарь с ID {client_id} добавил новую книгу c ID {result.id}")
        return result


class SERVICE_UpdateBook(BaseService):
    def __init__(
            self,
            update_book_repository: DB_UpdateBook = Depends()
    ):
        super().__init__()
        self._update_book_repository = update_book_repository

    async def __call__(self, client_id: ID, book_id: ID, model: INPUT_UpdateBook):
        result = await self._update_book_repository(book_id, model)
        logger.info(f"Библиотекарь с ID {client_id} обновил данные книги с ID {result.id}")
        return result


class SERVICE_GetBookById(BaseService):
    def __init__(
            self,
            get_book_by_id_repository: DB_GetBookById = Depends()
    ):
        super().__init__()
        self._get_book_by_id_repository = get_book_by_id_repository

    async def __call__(self, book_id: ID):
        result = await self._get_book_by_id_repository(book_id)
        return result


class SERVICE_GetBookList(BaseService):
    def __init__(
            self,
            get_book_list_repository: DB_GetBookList = Depends()
    ):
        super().__init__()
        self._get_book_list_repository = get_book_list_repository

    async def __call__(self, skip: int, limit: int):
        result = await self._get_book_list_repository(skip, limit)
        return result


class SERVICE_DeleteBook(BaseService):
    def __init__(
            self,
            delete_book_repository: DB_DeleteBook = Depends()
    ):
        super().__init__()
        self._delete_book_repository = delete_book_repository

    async def __call__(self, client_id: ID, book_id: ID):
        await self._delete_book_repository(book_id)
        logger.info(f"Библиотекарь с ID {client_id} удалил книгу с ID {book_id}")
