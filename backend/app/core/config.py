from dataclasses import dataclass
from os import getenv


@dataclass(frozen=True)
class Settings:
    app_name: str = "Hotel Operations Intelligence Agent API"
    environment: str = getenv("APP_ENV", "local")
    database_url: str = getenv("DATABASE_URL", "sqlite:///./hotel_ops.db")
    redis_url: str = getenv("REDIS_URL", "redis://localhost:6379/0")
    qdrant_url: str = getenv("QDRANT_URL", "http://localhost:6333")
    object_storage_endpoint: str = getenv("MINIO_ENDPOINT", "localhost:9000")
    auth_mode: str = getenv("AUTH_MODE", "disabled")
    jwt_secret: str = getenv("JWT_SECRET", "local-development-secret-change-before-production")
    jwt_audience: str = getenv("JWT_AUDIENCE", "hotel-ops-api")
    cors_origins: tuple[str, ...] = tuple(
        origin.strip()
        for origin in getenv("CORS_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173").split(
            ","
        )
        if origin.strip()
    )


settings = Settings()
