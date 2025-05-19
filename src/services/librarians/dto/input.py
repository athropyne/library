from pydantic import BaseModel, EmailStr, Field


class INPUT_CreateLibrarian(BaseModel):
    login: EmailStr = Field(..., description="Email библиотекаря")
    password: str = Field(..., description="Пароль библиотекаря")
