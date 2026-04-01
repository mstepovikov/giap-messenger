from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import Optional, List
from contextlib import contextmanager

from config import settings
from models import Base, User as UserModel, UserRole
from schemas import UserCreate, UserUpdate, UserStatus

# Создание движка базы данных
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # Для SQLite
)

# Создание сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Инициализация базы данных"""
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_db():
    """Получение сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class UserDB:
    """Класс для работы с пользователями в БД"""

    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[UserModel]:
        """Получение пользователя по ID"""
        return db.query(UserModel).filter(UserModel.id == user_id).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[UserModel]:
        """Получение пользователя по имени"""
        return db.query(UserModel).filter(UserModel.username == username).first()

    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[UserModel]:
        """Получение списка пользователей"""
        return db.query(UserModel).offset(skip).limit(limit).all()

    @staticmethod
    def get_users_by_department(db: Session, department: str) -> List[UserModel]:
        """Получение пользователей по отделу"""
        return db.query(UserModel).filter(UserModel.department == department).all()

    @staticmethod
    def create_user(db: Session, user: UserCreate) -> UserModel:
        """Создание нового пользователя"""
        db_user = UserModel(
            username=user.username,
            full_name=user.full_name,
            department=user.department,
            status=user.status.value,
            role=user.role.value
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[UserModel]:
        """Обновление пользователя"""
        db_user = UserDB.get_user(db, user_id)
        if db_user:
            update_data = user_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                if field == "status":
                    setattr(db_user, field, value.value if hasattr(value, 'value') else value)
                elif field == "role":
                    setattr(db_user, field, value.value if hasattr(value, 'value') else value)
                else:
                    setattr(db_user, field, value)
            db.commit()
            db.refresh(db_user)
        return db_user

    @staticmethod
    def update_user_status(db: Session, user_id: int, status: UserStatus) -> Optional[UserModel]:
        """Обновление статуса пользователя"""
        db_user = UserDB.get_user(db, user_id)
        if db_user:
            db_user.status = status.value
            db_user.last_seen = datetime.utcnow()
            db.commit()
            db.refresh(db_user)
        return db_user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Удаление пользователя"""
        db_user = UserDB.get_user(db, user_id)
        if db_user:
            db.delete(db_user)
            db.commit()
            return True
        return False

    @staticmethod
    def sync_from_ad(db: Session, ad_users: List[dict]) -> List[UserModel]:
        """Синхронизация пользователей из Active Directory"""
        synced_users = []
        for ad_user in ad_users:
            existing_user = UserDB.get_user_by_username(db, ad_user['username'])

            if existing_user:
                # Обновляем существующего пользователя
                existing_user.full_name = ad_user['full_name']
                existing_user.department = ad_user.get('department')
                db.add(existing_user)
                synced_users.append(existing_user)
            else:
                # Создаем нового пользователя
                new_user = UserModel(
                    username=ad_user['username'],
                    full_name=ad_user['full_name'],
                    department=ad_user.get('department'),
                    status="offline",
                    role="user"
                )
                db.add(new_user)
                synced_users.append(new_user)

        db.commit()
        return synced_users