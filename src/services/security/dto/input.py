from pydantic import BaseModel, Field


class INPUT_AuthData(BaseModel):
    login: str = Field(..., max_length=30)
    password: str = Field(..., max_length=100)
