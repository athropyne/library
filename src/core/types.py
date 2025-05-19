from pydantic import Field, BaseModel

ID = int


class IDModel(BaseModel):
    id: ID
