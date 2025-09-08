"""
Модели базы данных для {{ cookiecutter.package_name }}
"""
from uuid import uuid4

from enum import Enum

from sqlalchemy import Column, String, Float, DateTime, Text, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class TimestampMixin:
    """
    Миксин для добавления временных меток создания и обновления
    """
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class TaskStatus(str, Enum):
    """
    Статусы задач в системе
    """
    IN_PROGRESS = "in_progress"
    DONE = "done"
    FAILED = "failed"


class Task(Base, TimestampMixin):
    """
    Модель для хранения информации о входящих задачах
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(PostgresUUID(as_uuid=True), nullable=False, index=True, default=uuid4)
    message_id = Column(String(255), nullable=True, index=True)
    status = Column(SQLEnum(TaskStatus), nullable=False, default=TaskStatus.IN_PROGRESS, index=True)
    processing_time = Column(Float, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)


class TaskMetadata(Base, TimestampMixin):
    """
    Модель для хранения метаданных задач, приходящих из очереди
    """
    __tablename__ = "task_metadata"

    task_id = Column(PostgresUUID(as_uuid=True), primary_key=True)
    triggered_by = Column(PostgresUUID(as_uuid=True), nullable=False)
