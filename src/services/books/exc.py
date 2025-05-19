from src.core.exc import NoDataToUpdate, NotFound, ClientError
from src.core.types import ID


class ISBNAlreadyExists(NoDataToUpdate):
    def __init__(self, isbn: str):
        super().__init__(detail=f"Книга с ISBN {isbn} уже существует")


class BookNotFound(NotFound):
    def __init__(self, book_id: ID):
        super().__init__(detail=f"Книга с ID {book_id} не найдена")
