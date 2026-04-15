"""Application configuration using pydantic-settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    openrouter_api_key: str = ""
    openrouter_model: str = "qwen/qwen2.5-vl-72b-instruct"
    default_model: str = "openrouter"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
