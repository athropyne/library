from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.core.dependencies import D
from src.core.infrastructures import Database
from src.services.books.routes import book_router
from src.services.borrowed_books.routes import borrowed_book_router
from src.services.librarians.routes import librarian_router
from src.services.readers.routes import readers_router
from src.services.security.routes import security_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    database = D.database()
    app.dependency_overrides[Database] = lambda: database
    yield
    await database.engine.dispose()


app = FastAPI(
    lifespan=lifespan,
    title="Библиотека"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(security_router)
app.include_router(librarian_router)
app.include_router(book_router)
app.include_router(readers_router)
app.include_router(borrowed_book_router)
