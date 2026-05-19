from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import HttpUrl

class Settings(BaseSettings):
    DATABASE_URL: str
    BASE_URL: HttpUrl
    JWT_SECRET: str
    JWT_ALGORITHM: str
    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379
    TEST_DATABASE_URL: str
    RATE_LIMIT_MAX: int = 10
    RATE_LIMIT_WINDOW: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

Config = Settings()
