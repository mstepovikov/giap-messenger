import sqlite3
import datetime


# Функция для подключения к базе данных
def get_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row  # Чтобы обращаться к колонкам по именам
    return conn


# Создание всех таблиц (запустить один раз при старте)
def init_database():
    conn = get_connection()
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            department TEXT,
            status TEXT DEFAULT 'offline',
            last_seen TIMESTAMP
        )
    ''')

    # Таблица сообщений
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user TEXT NOT NULL,
            to_user TEXT NOT NULL,
            message TEXT,
            file_path TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_read INTEGER DEFAULT 0,
            message_type TEXT DEFAULT 'text'
        )
    ''')

    # Таблица для объявлений
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_by TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()


# Функции для работы с пользователями
def add_user(username, full_name, department):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (username, full_name, department, status, last_seen)
            VALUES (?, ?, ?, 'offline', ?)
        ''', (username, full_name, department, datetime.datetime.now()))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_user(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user


def update_status(username, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users SET status = ?, last_seen = ? WHERE username = ?
    ''', (status, datetime.datetime.now(), username))
    conn.commit()
    conn.close()


def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT username, full_name, department, status FROM users')
    users = cursor.fetchall()
    conn.close()
    return users


# Функции для работы с сообщениями
def save_message(from_user, to_user, message, file_path=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO messages (from_user, to_user, message, file_path, is_read)
        VALUES (?, ?, ?, ?, 0)
    ''', (from_user, to_user, message, file_path))
    conn.commit()
    message_id = cursor.lastrowid
    conn.close()
    return message_id


def mark_as_read(message_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE messages SET is_read = 1 WHERE id = ?', (message_id,))
    conn.commit()
    conn.close()


def get_unread_count(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) FROM messages 
        WHERE to_user = ? AND is_read = 0
    ''', (username,))
    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_messages_between(from_user, to_user, limit=50):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM messages 
        WHERE (from_user = ? AND to_user = ?) 
           OR (from_user = ? AND to_user = ?)
        ORDER BY timestamp DESC LIMIT ?
    ''', (from_user, to_user, to_user, from_user, limit))
    messages = cursor.fetchall()
    conn.close()
    return list(messages)


# Функции для объявлений
def save_announcement(title, content, created_by):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO announcements (title, content, created_by)
        VALUES (?, ?, ?)
    ''', (title, content, created_by))
    conn.commit()
    conn.close()


def get_announcements(limit=10):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM announcements ORDER BY timestamp DESC LIMIT ?
    ''', (limit,))
    announcements = cursor.fetchall()
    conn.close()
    return announcements