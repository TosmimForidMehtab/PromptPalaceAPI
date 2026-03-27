from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Pydantic will automatically look for a "DATABASE_URL" environment variable
    DATABASE_URL: str

    # You can still provide default fallback values
    JWT_SECRET_KEY: str = ""
    IMAGEKIT_PUBLIC_KEY: str = ""
    IMAGEKIT_PRIVATE_KEY: str = ""
    IMAGEKIT_URL_ENDPOINT: str = ""
    JWT_ALGORITHM: str = "HS256"

    # CORS allowed origins (comma-separated string)
    CORS_ALLOWED_ORIGINS: str = ""

    # Optional: If you are using a .env file, this tells Pydantic to read from it
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origins(self) -> list[str]:
        """Parse comma-separated CORS allowed origins into a list."""
        if not self.CORS_ALLOWED_ORIGINS:
            return []
        return [origin.strip() for origin in self.CORS_ALLOWED_ORIGINS.split(",") if origin.strip()]


settings = Settings()
