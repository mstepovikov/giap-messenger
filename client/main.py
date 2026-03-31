import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog, simpledialog
import threading
import websocket
import requests
import json
import os
import time
from datetime import datetime

# Импортируем настройки
import config

# Глобальные переменные (да, в начале так проще)
current_user = None
current_chat_with = None
ws = None
messages_cache = {}  # {username: [список сообщений]}
notifications_queue = []  # Очередь уведомлений


# --- Функции для работы с сервером ---

def login_to_server(username, password):
    """Отправка запроса на сервер для входа"""
    try:
        response = requests.post(
            f"{config.API_URL}/login",
            params={"username": username, "password": password}
        )
        result = response.json()
        if result.get("success"):
            return True, result
        else:
            return False, result.get("error", "Ошибка входа")
    except Exception as e:
        return False, str(e)


def get_users_list():
    """Получить список пользователей с сервера"""
    try:
        response = requests.get(f"{config.API_URL}/users")
        result = response.json()
        return result.get("users", [])
    except:
        return []


def get_messages_history(user1, user2):
    """Получить историю сообщений"""
    try:
        response = requests.get(
            f"{config.API_URL}/messages/{user1}/{user2}",
            params={"limit": 50}
        )
        result = response.json()
        return result.get("messages", [])
    except:
        return []


def get_unread_count(username):
    """Получить количество непрочитанных сообщений"""
    try:
        response = requests.get(f"{config.API_URL}/unread/{username}")
        result = response.json()
        return result.get("unread_count", 0)
    except:
        return 0


def send_announcement(title, content, created_by):
    """Отправить объявление"""
    try:
        response = requests.post(
            f"{config.API_URL}/announcement",
            params={"title": title, "content": content, "created_by": created_by}
        )
        return response.json()
    except:
        return {"success": False}


# --- Функции для WebSocket ---

def connect_websocket():
    """Подключение к WebSocket серверу"""
    global ws

    def on_message(ws_instance, message):
        """Обработка входящих сообщений через WebSocket"""
        try:
            data = json.loads(message)
            msg_type = data.get("type")

            if msg_type == "message":
                # Новое сообщение
                from_user = data.get("from")
                message_text = data.get("message")
                timestamp = data.get("timestamp")

                # Добавляем в кэш
                if from_user not in messages_cache:
                    messages_cache[from_user] = []
                messages_cache[from_user].append({
                    "from_user": from_user,
                    "message": message_text,
                    "timestamp": timestamp,
                    "is_read": False
                })

                # Показываем уведомление
                show_notification(from_user, message_text)

                # Если чат с этим пользователем открыт, обновляем окно
                if current_chat_with == from_user:
                    update_chat_display()
                else:
                    # Обновляем список чатов (показываем непрочитанные)
                    update_user_list()

            elif msg_type == "user_list":
                # Обновление списка пользователей
                update_user_list_gui(data.get("users", []))

            elif msg_type == "announcement":
                # Объявление
                title = data.get("title")
                content = data.get("content")
                show_notification(f"ОБЪЯВЛЕНИЕ: {title}", content)
                add_to_chat("system", f"--- {title} ---\n{content}\n---")

            elif msg_type == "typing":
                # Уведомление о наборе текста
                from_user = data.get("from")
                is_typing = data.get("is_typing")
                update_typing_indicator(from_user, is_typing)

        except Exception as e:
            print(f"Ошибка обработки сообщения: {e}")

    def on_error(ws_instance, error):
        print(f"WebSocket ошибка: {error}")

    def on_close(ws_instance, close_status_code, close_msg):
        print("WebSocket закрыт")
        # Пытаемся переподключиться через 5 секунд
        time.sleep(5)
        connect_websocket()

    ws_url = f"{config.WS_URL}/{current_user['username']}"
    ws = websocket.WebSocketApp(ws_url,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    # Запускаем в отдельном потоке
    ws_thread = threading.Thread(target=ws.run_forever, daemon=True)
    ws_thread.start()


def send_message(to_user, message_text):
    """Отправить сообщение через WebSocket"""
    if not ws:
        return

    message_data = {
        "type": "message",
        "to": to_user,
        "message": message_text
    }
    ws.send(json.dumps(message_data, ensure_ascii=False))


def send_typing_notification(to_user, is_typing):
    """Отправить уведомление о наборе текста"""
    if not ws:
        return

    typing_data = {
        "type": "typing",
        "to": to_user,
        "is_typing": is_typing
    }
    ws.send(json.dumps(typing_data))


def update_status(status):
    """Обновить статус пользователя"""
    if not ws:
        return

    status_data = {
        "type": "status_update",
        "status": status
    }
    ws.send(json.dumps(status_data))


# --- GUI функции ---

def show_notification(title, message):
    """Показать системное уведомление (рабочий стол)"""
    try:
        # Для Windows
        from win10toast import ToastNotifier
        toaster = ToastNotifier()
        toaster.show_toast(title, message, duration=5)
    except:
        # Если библиотека не установлена, выводим в консоль
        print(f"[УВЕДОМЛЕНИЕ] {title}: {message}")

        # Также можно использовать messagebox, но он блокирующий
        # Добавляем в очередь для отображения
        notifications_queue.append((title, message))


def update_user_list_gui(users):
    """Обновление списка пользователей в интерфейсе"""
    # Очищаем список
    user_listbox.delete(0, tk.END)

    # Сортируем: сначала онлайн, потом остальные
    online_users = []
    offline_users = []

    for user in users:
        if user['username'] == current_user['username']:
            continue  # Пропускаем себя

        status = user.get('status', 'offline')
        status_text = {
            'online': '🟢',
            'offline': '⚪',
            'away': '🟡',
            'dnd': '🔴'
        }.get(status, '⚪')

        display_text = f"{status_text} {user['full_name']} ({user['department']})"
        user_data = user

        if status == 'online':
            online_users.append((display_text, user_data))
        else:
            offline_users.append((display_text, user_data))

    # Добавляем в список
    for text, user_data in online_users + offline_users:
        user_listbox.insert(tk.END, text)
        # Сохраняем данные пользователя в атрибуте элемента списка
        index = user_listbox.size() - 1
        user_listbox.itemconfig(index, user_data=user_data)


def update_chat_display():
    """Обновить отображение чата"""
    if not current_chat_with:
        return

    # Очищаем область сообщений
    chat_area.delete(1.0, tk.END)

    # Получаем сообщения из кэша
    if current_chat_with in messages_cache:
        for msg in messages_cache[current_chat_with]:
            # Определяем, от кого сообщение
            if msg['from_user'] == current_user['username']:
                prefix = "Я: "
                color = "blue"
            elif msg['from_user'] == current_chat_with:
                prefix = f"{msg['from_user']}: "
                color = "black"
            else:
                continue

            # Форматируем сообщение
            timestamp = msg.get('timestamp', '')[:16]  # Обрезаем до минут
            chat_area.insert(tk.END, f"[{timestamp}] ", "timestamp")
            chat_area.insert(tk.END, f"{prefix}", "name")
            chat_area.insert(tk.END, f"{msg['message']}\n", "message")

    # Прокручиваем вниз
    chat_area.see(tk.END)

    # Помечаем сообщения как прочитанные
    mark_messages_as_read(current_chat_with)


def add_to_chat(sender, text):
    """Добавить сообщение в текущий чат (для системных сообщений)"""
    if not current_chat_with:
        return

    chat_area.insert(tk.END, f"{sender}: {text}\n", "system")
    chat_area.see(tk.END)


def on_user_select(event):
    """Обработка выбора пользователя из списка"""
    global current_chat_with

    selection = user_listbox.curselection()
    if not selection:
        return

    index = selection[0]
    user_data = user_listbox.itemconfig(index, 'user_data')
    selected_user = user_data[4]  # Получаем сохраненные данные

    current_chat_with = selected_user['username']

    # Загружаем историю сообщений
    load_chat_history(current_chat_with)

    # Обновляем заголовок окна
    chat_title.config(text=f"Чат с: {selected_user['full_name']} ({selected_user['department']})")

    # Активируем поле ввода
    message_entry.config(state='normal')
    send_button.config(state='normal')

    # Очищаем поле ввода
    message_entry.delete(0, tk.END)
    message_entry.focus()


def load_chat_history(username):
    """Загрузить историю сообщений с сервера"""
    messages = get_messages_history(current_user['username'], username)

    # Сохраняем в кэш
    messages_cache[username] = []
    for msg in messages:
        messages_cache[username].append({
            "from_user": msg['from_user'],
            "message": msg['message'],
            "timestamp": msg['timestamp'],
            "is_read": msg.get('is_read', False)
        })

    update_chat_display()


def mark_messages_as_read(username):
    """Пометить сообщения от пользователя как прочитанные"""
    # Здесь нужно отправить уведомление на сервер о прочтении
    if username in messages_cache:
        for msg in messages_cache[username]:
            if not msg['is_read'] and msg['from_user'] == username:
                msg['is_read'] = True
                # Отправляем уведомление о прочтении (упрощенно)
                if ws:
                    read_data = {
                        "type": "read_receipt",
                        "message_id": msg.get('id', 0),
                        "reader": current_user['username']
                    }
                    ws.send(json.dumps(read_data))


def send_message_gui(event=None):
    """Отправка сообщения из GUI"""
    if not current_chat_with:
        return

    message = message_entry.get().strip()
    if not message:
        return

    # Отправляем через WebSocket
    send_message(current_chat_with, message)

    # Добавляем в локальный кэш
    if current_chat_with not in messages_cache:
        messages_cache[current_chat_with] = []

    messages_cache[current_chat_with].append({
        "from_user": current_user['username'],
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "is_read": True
    })

    # Обновляем отображение
    update_chat_display()

    # Очищаем поле ввода
    message_entry.delete(0, tk.END)


def on_typing(event):
    """Обработка набора текста"""
    if current_chat_with and ws:
        send_typing_notification(current_chat_with, True)
        # Отменяем уведомление через 2 секунды после остановки набора
        root.after(2000, lambda: send_typing_notification(current_chat_with, False))


def update_typing_indicator(from_user, is_typing):
    """Обновление индикатора набора текста"""
    if current_chat_with == from_user:
        if is_typing:
            status_label.config(text=f"{from_user} печатает...")
        else:
            status_label.config(text="")


def show_announcement_dialog():
    """Показать диалог создания объявления"""
    title = simpledialog.askstring("Объявление", "Введите заголовок объявления:")
    if not title:
        return

    content = simpledialog.askstring("Объявление", "Введите текст объявления:")
    if not content:
        return

    send_announcement(title, content, current_user['full_name'])
    messagebox.showinfo("Успех", "Объявление отправлено")


def update_status_menu():
    """Показать меню выбора статуса"""
    status_window = tk.Toplevel(root)
    status_window.title("Выберите статус")
    status_window.geometry("200x150")

    def set_status(status):
        update_status(status)
        status_window.destroy()
        status_button.config(text=f"Статус: {status}")

    tk.Button(status_window, text="🟢 Онлайн", command=lambda: set_status("online")).pack(fill=tk.X, padx=10, pady=5)
    tk.Button(status_window, text="🟡 Отошел", command=lambda: set_status("away")).pack(fill=tk.X, padx=10, pady=5)
    tk.Button(status_window, text="🔴 Не беспокоить", command=lambda: set_status("dnd")).pack(fill=tk.X, padx=10, pady=5)
    tk.Button(status_window, text="⚪ Офлайн", command=lambda: set_status("offline")).pack(fill=tk.X, padx=10, pady=5)


# --- Окно входа ---

def show_login_window():
    """Окно аутентификации"""
    login_win = tk.Toplevel(root)
    login_win.title("Вход в мессенджер")
    login_win.geometry("300x200")
    login_win.transient(root)
    login_win.grab_set()

    tk.Label(login_win, text="Имя пользователя:").pack(pady=5)
    username_entry = tk.Entry(login_win)
    username_entry.pack(pady=5)

    tk.Label(login_win, text="Пароль:").pack(pady=5)
    password_entry = tk.Entry(login_win, show="*")
    password_entry.pack(pady=5)

    result_label = tk.Label(login_win, text="", fg="red")
    result_label.pack(pady=5)

    def do_login():
        username = username_entry.get()
        password = password_entry.get()

        if not username or not password:
            result_label.config(text="Введите имя и пароль")
            return

        success, result = login_to_server(username, password)
        if success:
            global current_user
            current_user = result
            login_win.destroy()
            start_main_interface()
        else:
            result_label.config(text=f"Ошибка: {result}")

    tk.Button(login_win, text="Войти", command=do_login).pack(pady=10)
    login_win.bind("<Return>", lambda e: do_login())


# --- Основной интерфейс ---

def start_main_interface():
    """Запуск основного окна после входа"""
    global user_listbox, chat_area, message_entry, send_button, chat_title, status_label, status_button, root

    # Очищаем основное окно
    for widget in root.winfo_children():
        widget.destroy()

    root.title(f"Мессенджер - {current_user['full_name']}")
    root.geometry("900x600")

    # Создаем меню
    menubar = tk.Menu(root)
    root.config(menu=menubar)

    tools_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Инструменты", menu=tools_menu)
    tools_menu.add_command(label="Сделать объявление", command=show_announcement_dialog)
    tools_menu.add_separator()
    tools_menu.add_command(label="Выход", command=root.quit)

    # Статусная строка
    status_frame = tk.Frame(root, bg="gray", height=30)
    status_frame.pack(fill=tk.X, side=tk.BOTTOM)

    status_label = tk.Label(status_frame, text="", bg="gray", fg="white")
    status_label.pack(side=tk.LEFT, padx=10)

    # Основной контейнер
    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Левая панель (список пользователей)
    left_frame = tk.Frame(main_frame, width=250)
    left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
    left_frame.pack_propagate(False)

    tk.Label(left_frame, text="Пользователи:", font=("Arial", 10, "bold")).pack(anchor=tk.W)

    user_listbox = tk.Listbox(left_frame, height=20)
    user_listbox.pack(fill=tk.BOTH, expand=True)
    user_listbox.bind("<<ListboxSelect>>", on_user_select)

    # Кнопка выбора статуса
    status_button = tk.Button(left_frame, text="Статус: онлайн", command=update_status_menu)
    status_button.pack(fill=tk.X, pady=5)

    # Правая панель (чат)
    right_frame = tk.Frame(main_frame)
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    chat_title = tk.Label(right_frame, text="Выберите пользователя", font=("Arial", 12, "bold"))
    chat_title.pack(anchor=tk.W, pady=5)

    # Область сообщений
    chat_area = scrolledtext.ScrolledText(right_frame, height=20, state='normal')
    chat_area.pack(fill=tk.BOTH, expand=True)

    # Настройка цветов для сообщений
    chat_area.tag_config("timestamp", foreground="gray", font=("Arial", 8))
    chat_area.tag_config("name", foreground="blue", font=("Arial", 9, "bold"))
    chat_area.tag_config("message", foreground="black")
    chat_area.tag_config("system", foreground="green", font=("Arial", 9, "italic"))

    # Панель ввода
    input_frame = tk.Frame(right_frame)
    input_frame.pack(fill=tk.X, pady=5)

    message_entry = tk.Entry(input_frame, state='disabled')
    message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    message_entry.bind("<KeyRelease>", on_typing)
    message_entry.bind("<Return>", send_message_gui)

    send_button = tk.Button(input_frame, text="Отправить", state='disabled', command=send_message_gui)
    send_button.pack(side=tk.RIGHT, padx=5)

    # Кнопка отправки файла
    file_button = tk.Button(input_frame, text="📎", width=3, command=lambda: None)  # Пока заглушка
    file_button.pack(side=tk.RIGHT, padx=2)

    # Загружаем список пользователей
    users = get_users_list()
    update_user_list_gui(users)

    # Подключаем WebSocket
    connect_websocket()

    # Таймер для проверки уведомлений
    def check_notifications():
        while notifications_queue:
            title, message = notifications_queue.pop(0)
            try:
                from win10toast import ToastNotifier
                toaster = ToastNotifier()
                toaster.show_toast(title, message, duration=5)
            except:
                pass
        root.after(1000, check_notifications)

    check_notifications()


# --- Запуск приложения ---

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Корпоративный мессенджер")
    root.geometry("400x300")

    # Показываем окно входа
    show_login_window()

    # Если вход не выполнен, закрываем приложение
    if not current_user:
        root.destroy()
    else:
        root.mainloop()