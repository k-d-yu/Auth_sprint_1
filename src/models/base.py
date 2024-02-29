import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID


class BaseMixin:
    id = Column(UUID(as_uuid=True),
                primary_key=True,
                default=uuid.uuid4,
                unique=True,
                nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)