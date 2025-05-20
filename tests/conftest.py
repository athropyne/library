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
async def finish():
    yield
    logger.warning("""
    Базы больше нет.
    Нет больше базы.
    Больше нет таблиц.
    Больше нет таблиц.
    Больше нет таблиц.
    """)
