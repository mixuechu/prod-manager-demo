from typing import List
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "制片管理系统"
    
    # CORS配置
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    # JWT配置
    SECRET_KEY: str = "your-secret-key-here"  # 请在生产环境中更改
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # 数据库配置
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///./prod_manager.db"
    
    # Azure OpenAI配置
    OPENAI_API_KEY: str = "f317dfd5256942ad873d3e13a1eb1dc7"
    OPENAI_API_VERSION: str = "2024-08-01-preview"
    OPENAI_API_ENDPOINT: str = "https://exbq.openai.azure.com/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-08-01-preview"
    OPENAI_MODEL_NAME: str = "gpt-4o-mini"
    
    # 文件存储配置
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 