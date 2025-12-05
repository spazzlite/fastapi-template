from typing import Optional, Sequence
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .base import BaseListOutModel


class UserBase(BaseModel):
    first_name: str = None
    last_name: str = None
    middle_name: Optional[str] = None


class UserCreateIn(UserBase):
    username: str
    password: str


class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDBBase(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_active: bool


class UserCreateOut(UserInDBBase):
    first_name: str | None
    last_name: str | None
    middle_name: str | None


class User(UserInDBBase):
    pass


class UserListOut(BaseListOutModel):
    items: Sequence[User] = []
