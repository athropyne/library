from fastapi import APIRouter, Depends
from starlette import status

from src.core.types import IDModel
from src.services.librarians.dto.input import INPUT_CreateLibrarian
from src.services.librarians.service import SERVICE_CreateLibrarian

librarian_router = APIRouter(prefix="/librarians", tags=["Библиотекари"])


@librarian_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового библиотекаря",
    description="""
    Функция регистрирует нового библиотекаря. 
    При успешной регистрации вернет ID библиотекаря.
    Если библиотекарь с данным email уже существует выбрасывает ошибку 400
    """,
    response_model=IDModel
)
async def create_librarian(
        model: INPUT_CreateLibrarian,
        service: SERVICE_CreateLibrarian = Depends()
):
    return await service(model)
