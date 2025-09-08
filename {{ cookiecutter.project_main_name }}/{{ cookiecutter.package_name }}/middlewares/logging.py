import time
import json
from typing import Optional
from uuid import UUID

from faststream import BaseMiddleware
from loguru import logger

from {{ cookiecutter.package_name }}.services.database import DatabaseService
from {{ cookiecutter.package_name }}.models import TaskStatus


class LoggingMiddleware(BaseMiddleware):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_service = DatabaseService()
        self._task_id: Optional[UUID] = None
        self.start_time: Optional[float] = None

    async def on_receive(self):
        self.start_time = time.monotonic()
        
        message_data = json.loads(self.msg.body.decode('utf-8'))
        task_id = UUID(message_data["task_id"])
        triggered_by = UUID(message_data["triggered_by"])
        
        logger.info(f"Message {self.msg.message_id} received - Task: {task_id}, Triggered by: {triggered_by}")
        
        task, is_new = await self.db_service.get_or_create_task(
            task_id=task_id,
            message_id=self.msg.message_id,
            triggered_by=triggered_by
        )
        
        self._task_id = task_id
        
        if is_new:
            logger.info(f"Created new task {task_id}")
        else:
            logger.info(f"Found existing task {task_id}, retry #{task.retry_count}")
        
        return await super().on_receive()

    async def after_processed(self, exc_type, exc_val, exc_tb):     # noqa
        duration = time.monotonic() - self.start_time
        
        status = TaskStatus.DONE if exc_type is None else TaskStatus.FAILED
        error_message = str(exc_val) if exc_val else None
        
        if status == TaskStatus.DONE:
            logger.info(f"Message {self.msg.message_id} processed successfully in {duration:.2f}s")
        else:
            logger.error(f"Message {self.msg.message_id} failed after {duration:.2f}s: {error_message}")
        
        if self._task_id:
            await self.db_service.update_task_status(
                task_id=self._task_id,
                status=status,
                processing_time=round(duration, 2),
                error_message=error_message
            )
            logger.info(f"Updated task {self._task_id} status to {status.value}")
        
        return await super().after_processed(exc_type, exc_val, exc_tb)
