from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional # Keep Optional if you plan to add optional settings later

class Settings(BaseSettings):
    PROJECT_NAME: str
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_SECRET_KEY: str
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30



    model_config = SettingsConfigDict(env_file=".env", extra='ignore')

settings = Settings()
