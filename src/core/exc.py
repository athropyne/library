from fastapi import HTTPException
from starlette import status


class NotFound(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ClientError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class AccessDenied(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class NotAuthorized(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class ExpiredSignatureError(NotAuthorized):
    def __init__(self):
        super().__init__(detail="Токен просрочен")


class InvalidTokenError(NotAuthorized):
    def __init__(self):
        super().__init__(detail="Неверный токен доступа")


class AlreadyExists(ClientError):
    ...


class NoDataToUpdate(ClientError):
    ...
