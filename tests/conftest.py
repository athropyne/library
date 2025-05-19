import asyncio
import platform

import pytest
from loguru import logger

from src.core.dependencies import D
from src.core.schemas import metadata

if platform.system() == "Windows":
    from asyncio import WindowsSelectorEventLoopPolicy

    asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())


@pytest.fixture(scope="module", autouse=True)
async def setup_db():
    database = D.database()
    await database.init(metadata)
    yield
    # сносим базу после чудо тестов
    async with database.engine.connect() as connection:
        await connection.run_sync(metadata.drop_all)
        await connection.commit()
        await database.engine.dispose()

    logger.warning("""
    Базы больше нет.
    Нет больше базы.
    Больше нет таблиц.
    Больше нет таблиц.
    Больше нет таблиц.
    """)
