import datetime

from pydantic import BaseModel, Field, EmailStr

from src.core.types import ID


class BorrowingBook(BaseModel):
    id: ID
    book_id: ID
    borrow_date: datetime.datetime


class OUTPUT_ReaderShortInfo(BaseModel):
    id: ID = Field(..., description="Идентификатор читателя")
    name: str = Field(..., max_length=100, description="Имя читателя")
    email: EmailStr = Field(..., max_length=360, description="Email читателя")


class OUTPUT_ReaderFullInfo(OUTPUT_ReaderShortInfo):
    borrowings: list[BorrowingBook] = Field(description="Задолженности")
