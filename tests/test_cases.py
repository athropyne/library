from asyncio import gather

import pytest
from httpx import ASGITransport, AsyncClient, Response

from src.app import app
from src.core.types import IDModel
from src.services.books.dto.input import INPUT_CreateBook
from src.services.borrowed_books.dto.input import INPUT_CreateBorrowedBook
from src.services.borrowed_books.exc import BorrowedLimitExceeded, ThereAreBorrowings, AllBooksBorrowed
from src.services.librarians.dto.input import INPUT_CreateLibrarian
from src.services.librarians.exc import LibrarianAlreadyExists
from src.services.readers.dto.input import INPUT_CreateReader


@pytest.fixture(scope="module", autouse=True)
async def get_client():
    async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.mark.asyncio
async def test_create_two_librarians(get_client):
    """"""
    logins = ["ioann.grozny@porn.hub", "piter001@xnxx.com"]
    models = [INPUT_CreateLibrarian(login=login, password="SuperSecretpaSSword") for login in logins]
    queries = [get_client.post("/librarians/", json=model.model_dump()) for model in models]
    expected_responses = [model.model_dump() for model in (IDModel(id=1), IDModel(id=2))]
    responses: list[Response] = await gather(*queries)
    parsed_responses = [response.json() for response in responses]

    def normalize(d):
        return tuple(sorted((k, v) for k, v in d.items()))

    assert sorted(parsed_responses, key=normalize) == sorted(expected_responses, key=normalize)


@pytest.mark.asyncio
async def test_double_create_librarians(get_client):
    login = "ioann.grozny@porn.hub"
    model = INPUT_CreateLibrarian(login=login, password="SuperSecretpaSSword")
    response = await get_client.post("/librarians/", json=model.model_dump())
    assert response.status_code == 400
    assert response.json() == {"detail": LibrarianAlreadyExists(login).detail}


@pytest.fixture(scope="module")
async def get_token(get_client):
    login = "ioann.grozny@porn.hub"
    password = "SuperSecretpaSSword"
    response = await get_client.post("/security/", data=dict(username=login, password=password))
    token = response.json()
    yield token["access_token"]


@pytest.mark.asyncio
async def test_create_readers(get_token, get_client):
    models = [
        INPUT_CreateReader(name="edwin hubble", email="big@gang.bang"),
        INPUT_CreateReader(name="stephen hawking", email="black@ass.hole")
    ]
    queries = [get_client.post("/readers/", headers={"Authorization": f"bearer {get_token}"}, json=model.model_dump())
               for model in models]
    expected_responses = [model.model_dump() for model in (IDModel(id=1), IDModel(id=2))]
    responses: list[Response] = await gather(*queries)
    parsed_responses = [response.json() for response in responses]

    def normalize(d):
        return tuple(sorted((k, v) for k, v in d.items()))

    assert sorted(parsed_responses, key=normalize) == sorted(expected_responses, key=normalize)


@pytest.mark.asyncio
async def test_create_books(get_token, get_client):
    models = [
        INPUT_CreateBook(
            title="Harry Potter and the dirty orgy",
            description=None,
            author="George Fisher Growling",
            year=666,
            ISBN="ISBN String",
            quantity=1,
        ),
        INPUT_CreateBook(
            title="Мастер и маргарин",
            description="""
                Это чудесное повествование о том как сатана печет блины, а мастер сломал фломастер.
            """,
            author="Михаил Шумахер",
            year=666,
            quantity=1,
        ),
        INPUT_CreateBook(
            title="Гарри поттер и принц полупокер в полуботинках",
            author="George Fisher Growling",
            year=666,
            ISBN=None,
            quantity=1,
        ),
        INPUT_CreateBook(
            title="Барак Обама. Как сбежать из кении в америку и стать президентом.",
            author="RealN*ggaMan",
            year=2026,
            quantity=1,
        ),
        INPUT_CreateBook(
            title="LurkMore",
            description="""
            You look a more yeah! 
            Doo-bop sale only Sly tired saved now Doo-bop Tom. 
            I'd know no chew Coat ouch only So cald it pass E. P. 
            Crow on.
            """,
            author="Alex under Sir gay evil each Pussy can",
            year=1488,
            ISBN="ISBN String",
            quantity=1,
        ),
    ]
    queries = [
        get_client.post(
            "/books/",
            headers={"Authorization": f"bearer {get_token}"},
            json=model.model_dump()
        )
        for model
        in models
    ]
    expected_responses = [
        model.model_dump()
        for model
        in [
            IDModel(id=i)
            for i
            in range(1, len(models) + 1)
        ]
    ]
    responses: list[Response] = await gather(*queries)
    parsed_responses = [response.json() for response in responses]

    def normalize(d):
        return tuple(sorted((k, v) for k, v in d.items()))

    assert sorted(parsed_responses, key=normalize) == sorted(expected_responses, key=normalize)


@pytest.mark.asyncio
async def test_give_out_3_books(get_token, get_client):
    reader_id = 1
    book_ids = 1, 2, 3
    models = [
        INPUT_CreateBorrowedBook(reader_id=reader_id, book_id=book_id)
        for book_id
        in book_ids
    ]
    queries = [
        get_client.post(
            "/borrowed_books/",
            headers={"Authorization": f"bearer {get_token}"},
            json=model.model_dump()
        )
        for model
        in models
    ]
    expected_responses = [
        model.model_dump()
        for model
        in [
            IDModel(id=i)
            for i
            in range(1, len(models) + 1)
        ]
    ]
    responses: list[Response] = await gather(*queries)
    parsed_responses = [response.json() for response in responses]

    def normalize(d):
        return tuple(sorted((k, v) for k, v in d.items()))

    assert sorted(parsed_responses, key=normalize) == sorted(expected_responses, key=normalize)


@pytest.mark.asyncio
async def test_give_out_1_books_over_limit(get_token, get_client):
    reader_id = 1
    book_id = 4
    model = INPUT_CreateBorrowedBook(reader_id=reader_id, book_id=book_id)
    response = await get_client.post(
        "/borrowed_books/",
        headers={"Authorization": f"bearer {get_token}"},
        json=model.model_dump()
    )
    assert response.status_code == 400
    assert response.json() == {"detail": BorrowedLimitExceeded(reader_id).detail}


@pytest.mark.asyncio
async def test_give_out_the_missing_book(get_token, get_client):
    reader_id = 2
    book_id = 1
    model = INPUT_CreateBorrowedBook(reader_id=reader_id, book_id=book_id)
    response = await get_client.post(
        "/borrowed_books/",
        headers={"Authorization": f"bearer {get_token}"},
        json=model.model_dump()
    )
    assert response.status_code == 400
    assert response.json() == {"detail": AllBooksBorrowed(book_id).detail}
