from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings for the application."""

    NODE_ENV: str = "development"

    SQLITE_DB_PATH: str = "./data/zele-econometric-models.db"
    PORT: int = 8000

    JWT_SECRET_KEY: str = "zele-econometric-models-secret-key-2026"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def validate(self) -> None:
        """Validate the settings."""
        if not self.JWT_SECRET_KEY:
            raise ValueError("The secret key is required")
        if not self.JWT_ALGORITHM:
            raise ValueError("The algorithm is required")
        if not self.JWT_ACCESS_TOKEN_EXPIRE_MINUTES:
            raise ValueError("The access token expire minutes is required")


settings = Settings()
