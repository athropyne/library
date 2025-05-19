from src.core.exc import NoDataToUpdate


class LibrarianAlreadyExists(NoDataToUpdate):
    def __init__(self, login: str):
        super().__init__(detail=f"Библиотекарь с логином {login} уже зарегистрирован")
