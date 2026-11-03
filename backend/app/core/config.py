import os
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "Printly API"
    ENVIRONMENT: str = "development" # development | production | testing
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/printly"
    SECRET_KEY: str = "super_secret_jwt_key_for_mvp"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    ALLOW_SUBDOMAIN_HEADER: bool = True
    
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    TURNSTILE_SECRET_KEY: str = "1x0000000000000000000000000000000AA"
    TURNSTILE_SITE_KEY: str = "1x00000000000000000000AA"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    def validate_production(self):
        if self.ENVIRONMENT == "production":
            if not self.SECRET_KEY or self.SECRET_KEY == "super_secret_jwt_key_for_mvp":
                raise ValueError("SECRET_KEY must be set securely in production environment!")
            if self.ALLOW_SUBDOMAIN_HEADER:
                raise ValueError("ALLOW_SUBDOMAIN_HEADER cannot be True in production!")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
