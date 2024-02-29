from uuid import UUID

from pydantic import BaseModel


class UserBaseModel(BaseModel):
    first_name: str
    last_name: str
    login: str


class UserCreate(UserBaseModel):
    password: str


class UserInDB(UserBaseModel):
    id: UUID

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    login: str
    password: str


class ChangePassword(BaseModel):
    current_password: str
    new_password: str
