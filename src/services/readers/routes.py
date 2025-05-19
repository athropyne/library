from fastapi import APIRouter, Depends
from starlette import status

from src.core.security import TokenManager
from src.core.types import ID, IDModel
from src.services.books.dto.input import HasBorrowings
from src.services.readers.dto.input import INPUT_CreateReader, INPUT_UpdateReader
from src.services.readers.dto.output import OUTPUT_ReaderShortInfo
from src.services.readers.service import SERVICE_CreateReader, SERVICE_GetReaderList, SERVICE_UpdateReader, \
    SERVICE_GetReaderById, SERVICE_DeleteReader

readers_router = APIRouter(prefix="/readers", tags=["Управление читателями"])


@readers_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Добавить читателя",
    description="""
    Функция регистрирует нового читателя.
    При дублировании email читателя вернет ошибку 400.
    Вернет ID читателя в случае успеха
    """,
    response_model=IDModel
)
async def create_reader(
        model: INPUT_CreateReader,
        service: SERVICE_CreateReader = Depends(),
        client_id: ID = Depends(TokenManager.decode)
):
    return await service(client_id, model)


@readers_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Получить список читателей",
    description="""
    Функция возвращает список читателей.
    Опция `borrowings` позволяет вернуть список по разному:
        с опцией `only with borrowings` вернет только тех читателей, у кого есть книги на руках,
        с опцией `only without borrowings` вернет только тех читателей, у кого нет книг на руках,
        с выключенной опцией вернет всех читателей.
    """,
    dependencies=[Depends(TokenManager.decode)],
    response_model=list[OUTPUT_ReaderShortInfo]
)
async def get_reader_list(
        borrowings: HasBorrowings | None = None,
        skip: int = 0,
        limit: int = 50,
        service: SERVICE_GetReaderList = Depends()
):
    return await service(borrowings, skip, limit)


@readers_router.put(
    "/{reader_id}",
    status_code=status.HTTP_200_OK,
    summary="Обновить данные читателя",
    description="""
    Функция обновляет данные читателя.
    При пустых данных вернет ошибку 400.
    При дублировании email читателя вернет ошибку 400.
    При отсутствии читателя вернет ошибку 401.
    Все ошибки с текстовыми пояснениями.
    Вернет ID читателя в случае успеха.
    """,
    response_model=IDModel
)
async def update_reader(
        reader_id: ID,
        model: INPUT_UpdateReader,
        service: SERVICE_UpdateReader = Depends(),
        client_id: ID = Depends(TokenManager.decode)
):
    return await service(client_id, reader_id, model)


@readers_router.get(
    "/{reader_id}",
    status_code=status.HTTP_200_OK,
    summary="Получить данные читателя",
    description="""
    Функция возвращает данные читателя с задолженностями.
    Если читатель не найден вернет ошибку 404.
    """,
    dependencies=[Depends(TokenManager.decode)],
)
async def get_reader_by_id(
        reader_id: ID,
        service: SERVICE_GetReaderById = Depends()
):
    return await service(reader_id)


@readers_router.delete(
    "/{reader_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить читателя",
    description="""
    Функция удаляет читателя.
    Читателя нельзя удалить если он торчит книжку. Вернет ошибку 400.
    Если читатель не найден вернет ошибку 404.
    """
)
async def delete_reader(
        reader_id: ID,
        service: SERVICE_DeleteReader = Depends(),
        client_id: ID = Depends(TokenManager.decode)
):
    await service(client_id, reader_id)
