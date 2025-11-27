from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import ClassVar
from pathlib import Path

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
    
    # --- Problem Settings ---
    # Get the project root directory
    PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent.parent
    PROBLEMS_DIR: Path = PROJECT_ROOT / "problems"
    
    def get_problem_path(self, problem_id: int) -> Path:
        """Get the path to a specific problem directory"""
        return self.PROBLEMS_DIR / f"problem{problem_id}"

# instance of the class to be used throughout the app
settings = Settings()