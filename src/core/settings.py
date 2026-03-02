from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings for the application."""

    SQLITE_DB_PATH: str = "./data/zele-econometric-models.db"

    JWT_SECRET_KEY: str = "zele-econometric-models-secret-key-2026"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

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
