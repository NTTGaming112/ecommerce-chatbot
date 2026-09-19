
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    PROJECT_NAME: str = "Simple RAG Service"
    GOOGLE_API_KEY: str = ""
    CHROMA_PERSIST_DIR: str = "./chroma_data"
    SQLITE_DB_PATH: str = "./data/chat_history.db"
    LLM_MODEL: str = "gemini-2.5-flash"
    LLM_TEMPERATURE: float = 0.0
    RETRIEVAL_K: int = 3
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    MIN_RETRIEVAL_SCORE: float = 0.45
    MAX_CONTEXT_CHARS: int = 12_000
    MAX_UPLOAD_BYTES: int = 10 * 1024 * 1024
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_BUFFER_TTL: int = 3600      # 1 hour
    REDIS_SUMMARY_TTL: int = 86400    # 24 hours
    REDIS_BUFFER_THRESHOLD: int = 10  # Auto-summarize khi buffer > 10 messages

    # Multi-Agent: Search Agent
    TAVILY_API_KEY: str = ""           # Web search via Tavily (optional)
    SEARCH_K: int = 5                  # Top-k docs to retrieve
    RERANK_ENABLED: bool = False       # Enable reranking (requires extra model)
    WEB_SEARCH_MAX_RESULTS: int = 3    # Max web results to return

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

settings = Settings()
