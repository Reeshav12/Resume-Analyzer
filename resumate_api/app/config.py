from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    database_url: str = os.environ.get("DATABASE_URL", "").strip()
    database_path: str = os.environ.get("DATABASE_PATH", "resumate_api.db")
    token_ttl_minutes: int = int(os.environ.get("TOKEN_TTL_MINUTES", "43200"))  # 30 days
    reset_token_ttl_minutes: int = int(os.environ.get("RESET_TOKEN_TTL_MINUTES", "15"))
    cors_origins: str = os.environ.get("CORS_ORIGINS", "*")
    ollama_api_key: str = os.environ.get("OLLAMA_API_KEY", "").strip()
    ollama_base_url: str = os.environ.get("OLLAMA_BASE_URL", "https://ollama.com/api").strip().rstrip("/")
    ollama_model: str = os.environ.get("OLLAMA_MODEL", "gpt-oss:120b").strip()
    ollama_timeout_seconds: int = int(os.environ.get("OLLAMA_TIMEOUT_SECONDS", "180"))


settings = Settings()
