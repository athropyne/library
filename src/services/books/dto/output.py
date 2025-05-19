from pydantic import BaseModel, Field, NonNegativeInt

from src.core.types import ID


class OUTPUT_BookFullInfo(BaseModel):
    id: ID = Field(..., description="Идентификатор книги")
    title: str = Field(..., description="Название книги")
    description: str | None = Field(None, description="Описание книги")
    author: str = Field(..., description="Автор")
    year: int | None = Field(None, description="Год издания")
    isbn: str | None = Field(None, description="ISBN")
    quantity: NonNegativeInt = Field(..., description="Количество")


class OUTPUT_BookShortInfo(BaseModel):
    id: ID = Field(..., description="Идентификатор книги")
    title: str = Field(..., description="Название книги")
    author: str = Field(..., description="Автор")
    year: int | None = Field(None, description="Год издания")
    is_available: bool = Field(..., description="В наличии или нет")
