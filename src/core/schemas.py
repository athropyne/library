import datetime

from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey, DateTime, Index

metadata = MetaData()

librarians = Table(
    "librarians",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("login", String(360), unique=True, nullable=False),
    Column("password", String(100), nullable=False)
)

books = Table(
    "books",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("title", String(100), nullable=False),
    Column("description", String(1000), nullable=True),
    Column("author", String(100), nullable=False),
    Column("isbn", String, nullable=True),
    Column("year", Integer, nullable=True),
    Column("quantity", Integer, nullable=False, default=1)
)

unique_isbn_idx = Index(
    "unique_isbn_idx_not_null",
    books.c.isbn,
    unique=True,
    postgresql_where=(books.c.isbn.isnot(None))
)

readers = Table(
    "readers",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(100), nullable=False),
    Column("email", String(360), unique=True, nullable=False)
)

borrowed_books = Table(
    "borrowed_books",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("book_id", ForeignKey(books.c.id, onupdate="CASCADE", ondelete="CASCADE"), nullable=False),
    Column("reader_id", ForeignKey(readers.c.id, onupdate="CASCADE", ondelete="CASCADE"), nullable=False),
    Column("borrow_date", DateTime, nullable=False, default=datetime.datetime.now),
    Column("return_date", DateTime, nullable=True, default=None)
)
