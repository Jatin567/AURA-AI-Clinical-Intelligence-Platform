from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    LLM_PROVIDER: str = "openai"  # "openai" | "gemini" | "ollama"
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_API_KEY: str = Field(default="", description="API key for cloud providers (optional for Ollama)")
    LLM_TIMEOUT_SECONDS: int = 30  # Increased default for local models
    LLM_MAX_TOKENS: int = 800

    # Ollama-specific configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/aura"
    FIREBASE_CREDENTIALS_PATH: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
