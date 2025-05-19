from pydantic import BaseModel, Field, EmailStr


class INPUT_CreateReader(BaseModel):
    name: str = Field(..., max_length=100, description="Имя читателя")
    email: EmailStr = Field(..., max_length=360, description="Email читателя")


class INPUT_UpdateReader(BaseModel):
    name: str | None = Field(None, max_length=100, description="Имя читателя")
    email: EmailStr | None = Field(None, max_length=360, description="Email читателя")
