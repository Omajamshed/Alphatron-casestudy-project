from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Root is 3 levels up from backend/app/core
BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):
    PROJECT_NAME: str = "ContractGuard"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str = "sqlite:///./contractguard.db"
    POSTGRES_DATABASE_URL: str = "postgresql+psycopg://contractguard:password@localhost:5432/contractguard"

    LLM_PROVIDER: str = "gemini"  # "gemini" | "claude" | "mock"
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gemini-2.5-flash"
    ANTHROPIC_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20241022"

    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    SIMILARITY_THRESHOLD: float = 0.35

    JWT_SECRET: str = "contractguard-super-secret-key-change-in-production-2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    MAX_UPLOAD_MB: int = 15
    UPLOAD_DIR: Path = BACKEND_DIR / "uploads"

    model_config = SettingsConfigDict(
        env_file=(PROJECT_ROOT / ".env", BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
