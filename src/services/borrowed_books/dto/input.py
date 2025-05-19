from pydantic import BaseModel
from pydantic.v1 import Field

from src.core.types import ID


class INPUT_CreateBorrowedBook(BaseModel):
    reader_id: ID = Field(..., description="ID читателя")
    book_id: ID = Field(..., description="ID книги")


class INPUT_ReturnBook(INPUT_CreateBorrowedBook):
    pass
