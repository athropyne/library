from fastapi import APIRouter, Depends
from starlette import status

from src.core.security import TokenManager
from src.core.types import ID, IDModel
from src.services.borrowed_books.dto.input import INPUT_CreateBorrowedBook, INPUT_ReturnBook
from src.services.borrowed_books.service import SERVICE_GiveOutBook, SERVICE_ReturnBook, SERVICE_GetBorrowList

borrowed_book_router = APIRouter(prefix="/borrowed_books", tags=["Выданные книги"])


@borrowed_book_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Выдать книгу",
    description="""
    Функция выдает книгу если у читателя менее 3х книг.
    Если у читателя уже есть такая книга вернет ошибку 400.
    Если читатель уже торчит 3 книги вернет ошибку 400.
    Если книга не найдена вернет ошибку 404.
    Если читатель не найден вернет ошибку 404.
    Если свободных книг нет или все на руках вернет 404.
    Все ошибки с текстовыми пояснениями.
    В случае успеха вернет ID записи аренды книги.
    """,
    response_model=IDModel
)
async def give_out_book(
        model: INPUT_CreateBorrowedBook,
        service: SERVICE_GiveOutBook = Depends(),
        client_id: ID = Depends(TokenManager.decode)
):
    return await service(client_id, model)


@borrowed_book_router.patch(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Вернуть книгу",
    description="""
    Функция забирает книгу у читателя и возвращает в библиотеку.
    Если у читателя книги нет или нет самого читателя или книги вернет 404.
    В в случае успеха не вернет ничего.
    """
)
async def return_book(
        model: INPUT_ReturnBook,
        service: SERVICE_ReturnBook = Depends(),
        client_id: ID = Depends(TokenManager.decode)
):
    return await service(client_id, model)


@borrowed_book_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Список задолженностей",
    description="""
    Функция возвращает список задолженностей.
    С включенной опцией `no_returned_only` возвращает только непогашенные.
    С выключенной возвращает все записи.
    Есть функционал пагинации SKIP/LIMIT.
    По умолчанию опция выключена.
    """,
    dependencies=[Depends(TokenManager.decode)]
)
async def get_borrow_list(
        skip: int = 0,
        limit: int = 50,
        no_returned_only: bool = False,
        service: SERVICE_GetBorrowList = Depends()
):
    return await service(skip, limit, no_returned_only)
