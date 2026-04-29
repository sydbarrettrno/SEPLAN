from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    DATABASE_URL: str = "sqlite:///./app.db"
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

@lru_cache
def get_settings() -> Settings:
    return Settings()
