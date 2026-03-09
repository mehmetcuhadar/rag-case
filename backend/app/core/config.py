'''
Reads environment variables (DATABASE_URL, OLLAMA_HOST, MODEL_NAME, etc.) via Pydantic Settings.
Single source of truth for config
'''

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # DB
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://mehmet:123456@db:5432/LLMAppDB"
    )

    # Ollama
    OLLAMA_HOST: str = Field(default="http://ollama:11434")
    MODEL_NAME: str = Field(default="qwen3:4b")

    # Chat behavior
    CHAT_HISTORY_LIMIT: int = Field(default=30)
    SYSTEM_PROMPT: str = Field(default="You are a helpful assistant.")

    # Server
    APP_NAME: str = Field(default="LLMApp Backend")

    # Auth
    JWT_SECRET: str = Field(default="CHANGE_ME")           # set in .env
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=14)

    # Hashing refresh tokens stored in DB (pepper)
    REFRESH_TOKEN_PEPPER: str = Field(default="CHANGE_ME_TOO")

    # Qdrant
    QDRANT_URL: str = Field(default="http://qdrant:6333")
    QDRANT_COLLECTION: str = Field(default="docs")

    # Embedding
    EMBEDDING_MODEL: str = Field(default="BAAI/bge-small-en-v1.5")
    EMBEDDING_DIM: int = Field(default=384)

    # Arxiv dataset
    ARXIV_DATASET: str = Field(default="nick007x/arxiv-papers")
    ARXIV_SUBJECT: str = Field(default="cs.AI")
    ARXIV_LIMIT: int = Field(default=10000)
    


settings = Settings()