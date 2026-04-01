from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    department = Column(String, nullable=True)
    status = Column(String, default="offline")  # offline, online, busy
    last_seen = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    role = Column(Enum(UserRole), default=UserRole.USER)

    def __repr__(self):
        return f"<User {self.username}>"