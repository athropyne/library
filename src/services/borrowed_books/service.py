from fastapi import Depends
from loguru import logger

from src.core.interfaces import BaseService
from src.core.types import ID
from src.services.borrowed_books.dto.input import INPUT_CreateBorrowedBook, INPUT_ReturnBook
from src.services.borrowed_books.repository import DB_GiveOutBook, DB_ReturnBook, DB_GetBorrowList


class SERVICE_GiveOutBook(BaseService):
    def __init__(
            self,
            give_out_book_repository: DB_GiveOutBook = Depends()
    ):
        super().__init__()
        self._give_out_book_repository = give_out_book_repository

    async def __call__(self, client_id: ID, model: INPUT_CreateBorrowedBook):
        result = await self._give_out_book_repository(model)
        logger.info(
            f"Библиотекарь с ID {client_id} выдал книгу читателю с ID {model.reader_id} книгу с ID {model.book_id}"
        )
        return result


class SERVICE_ReturnBook(BaseService):
    def __init__(
            self,
            return_book_repository: DB_ReturnBook = Depends()
    ):
        super().__init__()
        self._return_book_repository = return_book_repository

    async def __call__(self, client_id: ID, model: INPUT_ReturnBook):
        result = await self._return_book_repository(model)
        return result


class SERVICE_GetBorrowList(BaseService):
    def __init__(
            self,
            get_borrow_list_repository: DB_GetBorrowList = Depends()
    ):
        super().__init__()
        self._get_borrow_list_repository = get_borrow_list_repository

    async def __call__(self, skip: int, limit: int, no_returned_only: bool):
        result = await self._get_borrow_list_repository(skip, limit, no_returned_only)
        return result
