"""init

Revision ID: 1db74dd02218
Revises: 
Create Date: 2025-05-18 22:45:54.169634

"""
from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = '1db74dd02218'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'librarians',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('login', sa.String(360), unique=True, nullable=False),
        sa.Column('password', sa.String(100), nullable=False)
    )

    op.create_table(
        'books',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('title', sa.String(100), nullable=False),
        sa.Column('author', sa.String(100), nullable=False),
        sa.Column('isbn', sa.String(), nullable=True),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1')
    )

    op.create_index(
        'unique_isbn_idx_not_null',
        'books',
        ['isbn'],
        unique=True,
        postgresql_where=sa.text('isbn IS NOT NULL')
    )

    op.create_table(
        'readers',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('email', sa.String(360), unique=True, nullable=False)
    )

    op.create_table(
        'borrowed_books',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('book_id', sa.Integer, nullable=False),
        sa.Column('reader_id', sa.Integer, nullable=False),
        sa.Column('borrow_date', sa.DateTime(), nullable=False,
                  server_default=sa.func.now()),
        sa.Column('return_date', sa.DateTime(), nullable=True)
    )

    op.create_foreign_key(
        'fk_borrowed_books_book_id',
        'borrowed_books', 'books',
        ['book_id'], ['id'],
        onupdate='CASCADE', ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_borrowed_books_reader_id',
        'borrowed_books', 'readers',
        ['reader_id'], ['id'],
        onupdate='CASCADE', ondelete='CASCADE'
    )


def downgrade():
    op.drop_table('borrowed_books')
    op.drop_index('unique_isbn_idx_not_null', table_name='books')
    op.drop_table('readers')
    op.drop_table('books')
    op.drop_table('librarians')
