from src.core.exc import AccessDenied, ClientError, NotFound
from src.core.types import ID


class BorrowedLimitExceeded(ClientError):
    def __init__(self, reader_id: ID):
        super().__init__(detail=f"У читателя с ID {reader_id} превышен лимит взятых книг")


class ReaderAlreadyHasBook(ClientError):
    def __init__(self, reader_id: ID, book_id: ID):
        super().__init__(detail=f"У читателя с ID {reader_id} уже есть книга с ID {book_id}")


class ThereAreBorrowings(ClientError):
    def __init__(self, book_id: ID):
        super().__init__(detail=f"Книга с ID {book_id} есть на руках у читателей")


class BorrowNotFound(NotFound):
    def __init__(self, reader_id: ID, book_id: ID):
        super().__init__(detail=f"Задолженность читателя с ID {reader_id} книги с ID {book_id} не найдена")


class AllBooksBorrowed(ClientError):
    def __init__(self, book_id: ID):
        super().__init__(detail=f"Все книги с ID {book_id} на руках у читателей")
