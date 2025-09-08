"""
Сервис для работы с базой данных
"""
from typing import Optional
from uuid import UUID
from loguru import logger

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select, update
from sqlalchemy.orm import DeclarativeBase

from worker_example.models import Task, TaskMetadata, TaskStatus, Base
from worker_example.settings import DatabaseConfig


class DatabaseService:
    def __init__(self):
        self.db_config = DatabaseConfig()
        self.engine = create_async_engine(self.db_config.db_url)
        self.async_session = async_sessionmaker(
            self.engine, 
            class_=AsyncSession, 
            expire_on_commit=False
        )
    
    async def get_or_create_task(
        self, 
        task_id: UUID, 
        message_id: Optional[str] = None,
        triggered_by: UUID = None
    ) -> tuple[Task, bool]:
        """
        Получает существующую задачу или создает новую
        
        Arguments:
            task_id: Идентификатор задачи из сообщения
            message_id: Идентификатор сообщения из RabbitMQ
            triggered_by: UUID пользователя/системы, инициировавшей задачу
            
        Returns:
            tuple: (Task, is_new_task) - задача и флаг, новая ли это задача
        """
        async with self.async_session() as session:
            stmt = select(Task).where(Task.task_id == task_id)      # noqa
            result = await session.execute(stmt)
            existing_task = result.scalar_one_or_none()
            
            if existing_task:
                existing_task.retry_count += 1
                existing_task.status = TaskStatus.IN_PROGRESS
                await session.commit()
                await session.refresh(existing_task)
                return existing_task, False
            else:
                new_task = Task(
                    task_id=task_id,
                    message_id=message_id,
                    status=TaskStatus.IN_PROGRESS,
                    retry_count=0
                )
                session.add(new_task)
                await session.commit()
                await session.refresh(new_task)
                
                await self._create_metadata(session, new_task.task_id, triggered_by)
                await session.commit()
                
                return new_task, True
    
    async def update_task_status(
        self, 
        task_id: UUID, 
        status: TaskStatus, 
        processing_time: Optional[float] = None,
        error_message: Optional[str] = None
    ) -> Optional[Task]:
        """
        Обновляет статус задачи
        
        Arguments:
            task_id: Идентификатор задачи
            status: Новый статус
            processing_time: Время обработки в секундах
            error_message: Сообщение об ошибке
            
        Returns:
            Task: Обновленная задача или None, если не найдена
        """
        async with self.async_session() as session:
            stmt = select(Task).where(Task.task_id == task_id)      # noqa
            result = await session.execute(stmt)
            task = result.scalar_one_or_none()
            
            if task:
                task.status = status
                if processing_time is not None:
                    task.processing_time = processing_time
                if error_message is not None:
                    task.error_message = error_message
                
                await session.commit()
                await session.refresh(task)
                return task
            else:
                logger.error(f"Try to update status on non-existing task {task_id}")
            return None

    @staticmethod
    async def _create_metadata(session: AsyncSession, task_id: UUID, triggered_by: UUID):
        """
        Создает метаданные для задачи
        
        Arguments:
            session: Сессия базы данных
            task_id: UUID задачи
            triggered_by: UUID пользователя/системы
        """
        metadata = TaskMetadata(
            task_id=task_id,
            triggered_by=triggered_by
        )
        session.add(metadata)
    
    async def close(self):
        await self.engine.dispose()
