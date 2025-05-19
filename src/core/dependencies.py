from src.core.infrastructures import Database, database


class D:
    @staticmethod
    def database() -> Database:
        return database

