"""应用配置"""
from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    APP_NAME: str = "万创运维"
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = True

    # 数据库 - 开发用SQLite，生产切MySQL
    DATABASE_URL: str = "sqlite:///./venue.db"

    # JWT
    SECRET_KEY: str = "venue-system-secret-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时

    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]

    class Config:
        env_file = ".env"


settings = Settings()
