from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
from typing import Dict
import datetime

# Импортируем наши модули
import database
import auth

# Создаем приложение
app = FastAPI()

# Разрешаем запросы с любых адресов (для локальной сети)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализируем базу данных
database.init_database()

# Хранилище активных WebSocket соединений
# Формат: {username: websocket}
active_connections = {}

# Хранилище статусов пользователей
user_statuses = {}


# --- REST API эндпоинты ---

@app.post("/api/login")
async def login(username: str, password: str):
    """Аутентификация пользователя"""
    success, user_info = auth.authenticate_with_domain(username, password)

    if success:
        # Проверяем, есть ли пользователь в базе
        existing_user = database.get_user(username)
        if not existing_user:
            # Добавляем нового пользователя
            database.add_user(username, user_info['full_name'], user_info['department'])

        return {
            "success": True,
            "username": username,
            "full_name": user_info['full_name'],
            "department": user_info['department']
        }
    else:
        return {"success": False, "error": "Неверные учетные данные"}


@app.get("/api/users")
async def get_users():
    """Получить список всех пользователей"""
    users = database.get_all_users()
    return {"users": [dict(user) for user in users]}


@app.get("/api/messages/{username1}/{username2}")
async def get_messages(username1: str, username2: str, limit: int = 50):
    """Получить историю сообщений между двумя пользователями"""
    messages = database.get_messages_between(username1, username2, limit)
    return {"messages": [dict(msg) for msg in messages]}


@app.get("/api/unread/{username}")
async def get_unread_count(username: str):
    """Получить количество непрочитанных сообщений"""
    count = database.get_unread_count(username)
    return {"unread_count": count}


@app.post("/api/announcement")
async def create_announcement(title: str, content: str, created_by: str):
    """Создать объявление"""
    database.save_announcement(title, content, created_by)

    # Отправляем объявление всем подключенным пользователям
    announcement_data = {
        "type": "announcement",
        "title": title,
        "content": content,
        "created_by": created_by,
        "timestamp": str(datetime.datetime.now())
    }

    for username, websocket in active_connections.items():
        try:
            await websocket.send_text(json.dumps(announcement_data, ensure_ascii=False))
        except:
            pass

    return {"success": True}


@app.get("/api/announcements")
async def get_announcements():
    """Получить последние объявления"""
    announcements = database.get_announcements()
    return {"announcements": [dict(ann) for ann in announcements]}


# --- WebSocket обработка ---

@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    """Обработка WebSocket соединений"""
    await websocket.accept()

    # Сохраняем соединение
    active_connections[username] = websocket

    # Обновляем статус пользователя
    database.update_status(username, 'online')
    user_statuses[username] = 'online'

    # Рассылаем всем обновленный список пользователей
    await broadcast_user_list()

    try:
        while True:
            # Получаем сообщение от клиента
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Обрабатываем разные типы сообщений
            if message_data.get('type') == 'message':
                # Обычное сообщение
                await handle_message(username, message_data)
            elif message_data.get('type') == 'read_receipt':
                # Уведомление о прочтении
                await handle_read_receipt(message_data)
            elif message_data.get('type') == 'status_update':
                # Обновление статуса
                await handle_status_update(username, message_data)
            elif message_data.get('type') == 'typing':
                # Уведомление о наборе текста
                await handle_typing(username, message_data)

    except WebSocketDisconnect:
        # Пользователь отключился
        pass
    finally:
        # Очищаем при отключении
        if username in active_connections:
            del active_connections[username]

        # Обновляем статус
        database.update_status(username, 'offline')
        user_statuses[username] = 'offline'

        # Рассылаем обновленный список
        await broadcast_user_list()


async def handle_message(from_user, message_data):
    """Обработка отправленного сообщения"""
    to_user = message_data.get('to')
    message_text = message_data.get('message', '')
    file_path = message_data.get('file_path', None)

    # Сохраняем в базу данных
    message_id = database.save_message(from_user, to_user, message_text, file_path)

    # Формируем данные для отправки
    message_to_send = {
        "type": "message",
        "id": message_id,
        "from": from_user,
        "message": message_text,
        "file_path": file_path,
        "timestamp": str(datetime.datetime.now())
    }

    # Отправляем получателю, если он онлайн
    if to_user in active_connections:
        try:
            await active_connections[to_user].send_text(
                json.dumps(message_to_send, ensure_ascii=False)
            )
        except:
            pass

    # Отправляем отправителю подтверждение
    if from_user in active_connections:
        try:
            message_to_send["type"] = "message_sent"
            await active_connections[from_user].send_text(
                json.dumps(message_to_send, ensure_ascii=False)
            )
        except:
            pass


async def handle_read_receipt(message_data):
    """Обработка уведомления о прочтении"""
    message_id = message_data.get('message_id')
    reader = message_data.get('reader')

    # Отмечаем сообщение как прочитанное
    database.mark_as_read(message_id)

    # Получаем информацию о сообщении, чтобы узнать отправителя
    # (для простоты пока пропускаем, но в реальном проекте нужно добавить функцию в database.py)

    # Уведомляем отправителя о прочтении
    # (требуется доработка)


async def handle_status_update(username, message_data):
    """Обновление статуса пользователя"""
    new_status = message_data.get('status')
    if new_status in ['online', 'offline', 'away', 'dnd']:
        user_statuses[username] = new_status
        database.update_status(username, new_status)
        await broadcast_user_list()


async def handle_typing(from_user, message_data):
    """Уведомление о наборе текста"""
    to_user = message_data.get('to')

    if to_user in active_connections:
        typing_data = {
            "type": "typing",
            "from": from_user,
            "is_typing": message_data.get('is_typing', False)
        }
        try:
            await active_connections[to_user].send_text(
                json.dumps(typing_data, ensure_ascii=False)
            )
        except:
            pass


async def broadcast_user_list():
    """Отправить всем пользователям актуальный список пользователей"""
    users = []
    for user in database.get_all_users():
        user_dict = dict(user)
        user_dict['status'] = user_statuses.get(user_dict['username'], user_dict['status'])
        users.append(user_dict)

    user_list_data = {
        "type": "user_list",
        "users": users
    }

    for username, websocket in active_connections.items():
        try:
            await websocket.send_text(json.dumps(user_list_data, ensure_ascii=False))
        except:
            pass

# Запуск сервера:
# uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload