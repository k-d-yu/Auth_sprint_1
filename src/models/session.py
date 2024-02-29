import uuid
from models.base import BaseMixin
from db.postgres import Base
from sqlalchemy import Column, String, ForeignKey


class Session(Base, BaseMixin):
    __tablename__ = 'users_sessions'

    user_id = Column(ForeignKey('users.id'))
    user_agent = Column(String(255))
    details = Column(String(255))

    def __init__(self, user_id: uuid, user_agent: str, details: str = '') -> None:
        self.user_id = user_id
        self.user_agent = user_agent
        self.details = details

    def __repr__(self) -> str:
        return f'<Session {self.id}>'
