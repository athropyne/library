from fastapi import Depends

from src.core.interfaces import BaseService
from src.core.security import PasswordManager
from src.services.librarians.dto.input import INPUT_CreateLibrarian
from src.services.librarians.repository import DB_CreateLibrarian


class SERVICE_CreateLibrarian(BaseService):
    def __init__(
            self,
            create_librarian_repository: DB_CreateLibrarian = Depends()
    ):
        super().__init__()
        self._create_librarian_repository = create_librarian_repository

    async def __call__(self, model: INPUT_CreateLibrarian):
        model.password = PasswordManager.hash(model.password)
        result = await self._create_librarian_repository(model)
        return result
