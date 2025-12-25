import os
from pydantic_settings import BaseSettings
from typing import Literal
from pydantic import ConfigDict


class Settings(BaseSettings):
    postgres_host: str
    postgres_port: int
    postgres_db: str
    postgres_user: str
    postgres_password: str
    database_url: str

    jwt_secret_access: str
    jwt_secret_refresh: str

    redis_url: str

    app_env: Literal["dev", "test", "prod"]
    app_debug: str

    model_config = ConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        env_file_encoding="utf-8"
    )


settings = Settings()
