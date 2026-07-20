from functools import lru_cache
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AI Data Analyst"
    groq_api_key: str | None = None
    groq_model: str = "llama-3.3-70b-versatile"
    max_rows_preview: int = 10

    model_config = ConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
