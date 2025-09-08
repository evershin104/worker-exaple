import os
from pydantic_settings import BaseSettings


from typing import Optional


class RabbitBrokerConfig(BaseSettings):
    RABBITMQ_HOST: Optional[str] = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_PORT: Optional[int] = int(os.getenv("RABBITMQ_PORT", "5672"))
    RABBITMQ_DEFAULT_USER: Optional[str] = os.getenv("RABBITMQ_DEFAULT_USER", "guest")
    RABBITMQ_DEFAULT_PASS: Optional[str] = os.getenv("RABBITMQ_DEFAULT_PASS", "guest")

    @property
    def rabbitmq_url(self):
        return (f"amqp://{self.RABBITMQ_DEFAULT_USER}:{self.RABBITMQ_DEFAULT_PASS}@"
                f"{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/")

    class Config:
        env_file_encoding = "utf-8"
        extra = "ignore"


class DatabaseConfig(BaseSettings):
    POSTGRES_DB: Optional[str] = os.getenv("POSTGRES_DB", "worker_example")
    POSTGRES_USER: Optional[str] = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: Optional[str] = os.getenv("POSTGRES_PASSWORD", "password")
    POSTGRES_PORT: Optional[str] = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_HOST: Optional[str] = os.getenv("POSTGRES_HOST", "localhost")

    @property
    def db_url(self) -> str:
        return (f"postgresql+asyncpg://{self.POSTGRES_USER}:"
                f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
                f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


broker_config = RabbitBrokerConfig()
db_config = DatabaseConfig()
