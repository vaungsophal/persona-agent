from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    aws_region: str = "ap-southeast-1"
    bedrock_model_id: str = "anthropic.claude-sonnet-20240620-v1:0"

    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None

    github_username: str = "vaungsophal"

    cors_origins: list[str] = ["*"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
