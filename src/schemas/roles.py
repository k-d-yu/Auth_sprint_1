from uuid import UUID

from pydantic import BaseModel


class RoleInfo(BaseModel):
    title: str


class DBRole(RoleInfo):
    id: UUID

    class Config:
        from_attributes = True


class DBUserRole(BaseModel):
    login: str

    roles: list[str]

    class Config:
        from_attributes = True
