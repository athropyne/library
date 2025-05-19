from fastapi import APIRouter, Depends
from starlette import status

from src.core import utils
from src.services.security.dto.input import INPUT_AuthData
from src.services.security.dto.output import OUTPUT_TokenModel
from src.services.security.service import SERVICE_Auth

security_router = APIRouter(prefix="/security", tags=["Безопасность"])


@security_router.post(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Аутентифицироваться",
    description="""
    Функция аутентификации пользователя. 
    При валидных данных возвращает `access_token` - токен доступа и `refresh_token` - токен обновления.
    При неверных данных вернет ошибку 400.
    """,
    response_model=OUTPUT_TokenModel,
)
async def auth(
        model: INPUT_AuthData = Depends(utils.convert_auth_data),
        service: SERVICE_Auth = Depends(SERVICE_Auth)
):
    return await service(model)
