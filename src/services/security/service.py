from fastapi import Depends

from src.core.interfaces import BaseService
from src.core.security import PasswordManager, TokenManager, TokenTypes
from src.services.security.dto.input import INPUT_AuthData
from src.services.security.dto.output import OUTPUT_TokenModel
from src.services.security.exc import InvalidLoginOrPassword
from src.services.security.repository import SQL_DB_GetUserByLogin


class SERVICE_Auth(BaseService):
    def __init__(self, repository: SQL_DB_GetUserByLogin = Depends()):
        super().__init__()
        self.repository = repository

    async def __call__(self, model: INPUT_AuthData):
        result = await self.repository.__call__(model.login)
        if result is not None:
            if not PasswordManager.verify(model.password, result["password"]):
                raise InvalidLoginOrPassword
            access_token = TokenManager.create({"id": str(result["id"])}, TokenTypes.ACCESS)
            refresh_token = TokenManager.create({"id": str(result["id"])}, TokenTypes.REFRESH)
            return OUTPUT_TokenModel(
                access_token=access_token,
                refresh_token=refresh_token
            )
