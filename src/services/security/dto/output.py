from pydantic import BaseModel


class OUTPUT_TokenModel(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    refresh_token: str
