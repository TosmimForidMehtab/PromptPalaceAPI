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

    # Optional: If you are using a .env file, this tells Pydantic to read from it
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
