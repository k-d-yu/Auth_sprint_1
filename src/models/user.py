from typing import List

from sqlalchemy.ext.asyncio import AsyncAttrs

from models.base import BaseMixin
from models.session import Session
from models.role import Role, association_table
from db.postgres import Base
from sqlalchemy import Column, String, select
from sqlalchemy.orm import Mapped, relationship
from werkzeug.security import check_password_hash, generate_password_hash


class User(AsyncAttrs, Base, BaseMixin):
    __tablename__ = 'users'
    login = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    roles: Mapped[List['Role']] = relationship(secondary=association_table)
    sessions: Mapped[list['Session']] = relationship()

    def __init__(self, login: str, password: str, first_name: str, last_name: str) -> None:
        self.login = login
        self.password = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def __repr__(self) -> str:
        return f'<User {self.login}>'



