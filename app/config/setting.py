"""
Context from Code Snippet E:/Projects/Python/binary-owl-python-backend/app/api/__init__.py
"""
from functools import lru_cache

# from pydantic import BaseSettings
from pydantic.v1 import BaseSettings

__all__ = (
    'Settings',
    'get_settings',
)


class Settings(BaseSettings):

    MONGODB_USERNAME: str
    MONGODB_PASSWORD: str
    MONGODB_URI: str
    MONGODB_DB: str
    MONGODB_PORT: int
    MONGODB_AUTHENTICATION_SOURCE: str

    APP_NO: str
    
    MAIL_HOST: str
    MAIL_PORT: int
    MAIL_USERNAME: str
    MAIL_PASSWORD: str

    FILE_PASSWORD: str

    COOKIE_KEY: str



    class Config:
        env_file = '.env'


@lru_cache()
def get_settings() -> Settings:
    return Settings()
