import os
from pathlib import Path

from sqlalchemy.engine import URL

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=False)


def _required_setting(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Required environment setting {name} is missing")
    return value


class Settings:
    # --- Database ---
    DB_USER: str = _required_setting("DB_USER")
    DB_PASSWORD: str = _required_setting("DB_PASSWORD")
    DB_HOST: str = _required_setting("DB_HOST")
    DB_PORT: int = int(_required_setting("DB_PORT"))
    DB_NAME: str = _required_setting("DB_NAME")

    @property
    def DATABASE_URL(self) -> URL:
        return URL.create(
            "mysql+pymysql",
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_NAME,
        )

    # --- JWT ---
    SECRET_KEY: str = _required_setting("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    if len(SECRET_KEY) < 32:
        raise RuntimeError("SECRET_KEY must contain at least 32 characters")

    # --- App ---
    APP_NAME: str = "Mini Banking System API"
    APP_VERSION: str = "1.0.0"

settings = Settings()