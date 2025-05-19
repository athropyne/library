from fastapi import APIRouter, Depends
from starlette import status

from src.core.security import TokenManager
from src.core.types import ID, IDModel
from src.services.books.dto.input import INPUT_CreateBook, INPUT_UpdateBook
from src.services.books.dto.output import OUTPUT_BookFullInfo, OUTPUT_BookShortInfo
from src.services.books.service import SERVICE_CreateBook, SERVICE_UpdateBook, SERVICE_GetBookById, SERVICE_DeleteBook, \
    SERVICE_GetBookList

book_router = APIRouter(prefix="/books", tags=["Книги"])


@book_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Добавить книгу",
    description="""
    Функция добавляет новую книгу в библиотеку.
    При успешном добавлении книги возвращается ее ID.
    При добавлении книги с одинаковым ISBN поднимет ошибку 400.
    Можно добавить одинаковые книги с разными ISBN (разные тиражи одной и той же книги) 
    или не указывать ISBN вообще.
    """,
)
async def create_book(
        model: INPUT_CreateBook,
        service: SERVICE_CreateBook = Depends(),
        client_id: ID = Depends(TokenManager.decode)
):
    return await service(client_id, model)


@book_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Получить список книг",
    description="""
    Функция возвращает список книг.
    Есть функционал SKIP/LIMIT для пагинации.
    Авторизация не обязательна.
    (читатели могут например в отдельном терминале посмотреть "меню" библиотеки чтобы выбрать себе че нить).
    Так же есть информация о наличии книги (о возможности ее взять) - поле `is_available`.
    Если `is_available` = true - книга есть в наличии, если false - все экземпляры на руках или такой книги вообще нет
    """,
    response_model=list[OUTPUT_BookShortInfo]
)
async def get_book_list(
        skip: int = 0,
        limit: int = 50,
        service: SERVICE_GetBookList = Depends()
):
    return await service(skip, limit)


@book_router.put(
    "/{book_id}",
    status_code=status.HTTP_200_OK,
    summary="Обновить данные книги",
    description="""
    Функция обновляет данные книги.
    При успешном обновлении вернет ID обновленной книги.
    При дублировании ISBN вернет ошибку 400.
    При пустых данных для обновления вернет ошибку 400.
    Возвращает 404 если книга не найдена.
    Ошибки с текстовым пояснением.
    """,
    response_model=IDModel
)
async def update_book(
        book_id: ID,
        model: INPUT_UpdateBook,
        service: SERVICE_UpdateBook = Depends(),
        client_id: ID = Depends(TokenManager.decode)
):
    return await service(client_id, book_id, model)


@book_router.get(
    "/{book_id}",
    status_code=status.HTTP_200_OK,
    summary="Получить данные книги",
    description="""
    Функция возвращает данные книги.
    Авторизация не обязательна 
    (читатели могут например в отдельном терминале посмотреть подробности о книге).
    Возвращает 404 если книга не найдена.
    """,
    response_model=OUTPUT_BookFullInfo
)
async def get_book_by_id(
        book_id: ID,
        service: SERVICE_GetBookById = Depends()
):
    return await service(book_id)


@book_router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить книгу",
    description="""
    Функция удаляет книгу из библиотеки.
    Книгу нельзя удалить если какие то экземпляры у читателей на руках.
    Возвращает 404 если книга не найдена.
    Возвращает 400 если книга есть у кого то на руках.
    Не возвращает ничего в случае успеха.
    """
)
async def delete_book(
        book_id: ID,
        service: SERVICE_DeleteBook = Depends(),
        client_id: ID = Depends(TokenManager.decode)
):
    return await service(client_id, book_id)
