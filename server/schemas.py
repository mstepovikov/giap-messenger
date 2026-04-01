from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class UserStatus(str, Enum):
    OFFLINE = "offline"
    ONLINE = "online"
    BUSY = "busy"


# Базовые схемы
class UserBase(BaseModel):
    username: str
    full_name: str
    department: Optional[str] = None
    status: UserStatus = UserStatus.OFFLINE
    role: UserRole = UserRole.USER


# Схема для создания пользователя
class UserCreate(UserBase):
    pass


# Схема для обновления пользователя
class UserUpdate(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    department: Optional[str] = None
    status: Optional[UserStatus] = None
    role: Optional[UserRole] = None


# Схема для ответа API
class UserResponse(UserBase):
    id: int
    last_seen: datetime

    class Config:
        from_attributes = True


# Схема для обновления статуса
class UserStatusUpdate(BaseModel):
    status: UserStatus