from enum import Enum

from pydantic import BaseModel, Field, NonNegativeInt


class HasBorrowings(str, Enum):
    only_with = "only with borrowings"
    only_without = "only without borrowings"


class INPUT_CreateBook(BaseModel):
    title: str = Field(..., max_length=100, description="Название книги")
    description: str | None = Field(None, max_length=1000, description="Описание книги")
    author: str = Field(..., max_length=100, description="Автор")
    year: int | None = Field(None, description="Год издания")
    isbn: str | None = Field(None, description="ISBN")
    quantity: NonNegativeInt = Field(1, description="Количество")


class INPUT_UpdateBook(BaseModel):
    title: str | None = Field(None, max_length=100, description="Название книги")
    description: str | None = Field(None, max_length=1000, description="Описание книги")
    author: str | None = Field(None, max_length=100, description="Автор")
    year: int | None = Field(None, description="Год издания")
    isbn: str | None = Field(None, description="ISBN")
    quantity: NonNegativeInt | None = Field(None, description="Количество")
