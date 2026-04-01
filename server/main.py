from fastapi import FastAPI, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db, init_db, UserDB
from schemas import UserCreate, UserUpdate, UserResponse, UserStatusUpdate, UserRole

app = FastAPI(title="User Management API", version="1.0.0")


# Инициализация базы данных при запуске
@app.on_event("startup")
async def startup_event():
    init_db()


# Middleware для обновления last_seen
@app.middleware("http")
async def update_last_seen(request, call_next):
    response = await call_next(request)
    return response


# Эндпоинты API
@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Создание нового пользователя"""
    existing_user = UserDB.get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует"
        )
    return UserDB.create_user(db, user)


@app.get("/users/", response_model=List[UserResponse])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получение списка пользователей"""
    users = UserDB.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=UserResponse)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    """Получение пользователя по ID"""
    user = UserDB.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return user


@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """Обновление данных пользователя"""
    user = UserDB.update_user(db, user_id, user_update)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return user


@app.patch("/users/{user_id}/status", response_model=UserResponse)
async def update_user_status(user_id: int, status_update: UserStatusUpdate, db: Session = Depends(get_db)):
    """Обновление статуса пользователя"""
    user = UserDB.update_user_status(db, user_id, status_update.status)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return user


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Удаление пользователя"""
    deleted = UserDB.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )


@app.get("/users/department/{department}", response_model=List[UserResponse])
async def get_users_by_department(department: str, db: Session = Depends(get_db)):
    """Получение пользователей по отделу"""
    users = UserDB.get_users_by_department(db, department)
    return users


@app.post("/users/sync-from-ad", response_model=List[UserResponse])
async def sync_from_ad(db: Session = Depends(get_db)):
    """Синхронизация с Active Directory (пример)"""
    # Здесь должна быть логика получения данных из AD
    # Это пример данных
    ad_users = [
        {
            "username": "ivanov_ii",
            "full_name": "Иванов Иван Иванович",
            "department": "IT Department"
        },
        {
            "username": "petrov_pp",
            "full_name": "Петров Петр Петрович",
            "department": "HR Department"
        }
    ]

    synced_users = UserDB.sync_from_ad(db, ad_users)
    return synced_users


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


# cd server переходим в директорию server
# uvicorn main:app --reload запускаем сервер для остановки ctrl+C
# cd .. возвращаемся на директорию выше