from models.base import BaseMixin
from sqlalchemy import Column, String, ForeignKey, Table

from db.postgres import Base


association_table = Table(
    "users_roles",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("role_id", ForeignKey("roles.id"), primary_key=True),
)


class Role(Base, BaseMixin):
    __tablename__ = 'roles'

    title = Column(String(64))

    def __init__(self, title: str) -> None:
        self.title = title

    def __repr__(self) -> str:
        return f'<Role {self.title}>'
