from pydantic import EmailStr

from src.core.exc import AlreadyExists, NotFound, ClientError
from src.core.types import ID


class ReaderAlreadyExists(AlreadyExists):
    def __init__(self, email: EmailStr):
        super().__init__(detail=f"Читатель c email {email} уже существует")
        

class ReaderNotFound(NotFound):
    def __init__(self, reader_id: ID):
        super().__init__(detail=f"Читатель с ID {reader_id} не найден")

class ReaderHasDebts(ClientError):
    def __init__(self, reader_id: ID):
        super().__init__(detail=f"Читателя нельзя удалить пока он должен книги")
