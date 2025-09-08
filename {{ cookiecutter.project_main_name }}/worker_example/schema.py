from uuid import UUID

from pydantic import BaseModel


class Payload(BaseModel):
    """ Detailed schema for message in queue """
    task_id: UUID
    triggered_by: UUID  # user
    ...
