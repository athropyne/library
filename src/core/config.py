from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='../.env', env_file_encoding='utf-8')

    # server
    SERVER_HOST: str = "localhost"
    SERVER_PORT: int = 10000

    # databases
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "library_manager"
    DB_SOCKET: str = "localhost"
    DB_LOGS: bool = True

    # token config
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_HOURS: int = 24 * 15
    TOKEN_SECRET_KEY: str = "abracadabra"


settings = Settings()
