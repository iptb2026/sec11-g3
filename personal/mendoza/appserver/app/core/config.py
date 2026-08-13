class Settings:
    # --- Database ---
    DB_USER: str = "admin"
    DB_PASSWORD: str = "1234"
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_NAME: str = "mendoza"

    # --- JWT ---
    SECRET_KEY: str = "..."
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # --- App ---
    APP_NAME: str = "Mini Banking System API"
    APP_VERSION: str = "1.0.0"


settings = Settings()
