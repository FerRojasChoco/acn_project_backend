from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import ClassVar

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

    # --- Database Settings ---
    DATABASE_URL: str

    # --- Authentication Settings ---
    SECRET_KEY: str
    ALGORITHM: str

# instance of the class  to be used throughout the app
settings = Settings()
