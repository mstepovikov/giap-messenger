import customtkinter as ctk
from datetime import datetime
from PIL import Image
import os

# Настройка темы
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class ModernMessenger:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Chat")
        self.root.geometry("1200x750")
        self.root.minsize(1000, 600)

        # Цвета
        self.bg_color = "#f0f2f5"
        self.sidebar_bg = "#ffffff"
        self.chat_bg = "#ffffff"
        self.user_msg_bg = "#e7f3ff"
        self.other_msg_bg = "#f0f2f5"
        self.hover_color = "#e9ecef"

        # Создание интерфейса
        self.create_main_layout()

        # Добавляем примеры данных
        self.add_example_data()

        # Запускаем анимацию печатания
        self.animate_typing()

    def create_main_layout(self):
        """Создание основного макета"""
        # Основной контейнер
        self.main_frame = ctk.CTkFrame(self.root, fg_color=self.bg_color)
        self.main_frame.pack(fill="both", expand=True)

        # Левая панель (список чатов)
        self.create_sidebar()

        # Правая панель (основной чат)
        self.create_chat_area()

    def create_sidebar(self):
        """Создание боковой панели"""
        self.sidebar = ctk.CTkFrame(
            self.main_frame,
            width=320,
            fg_color=self.sidebar_bg,
            corner_radius=0
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Заголовок "Chat"
        header_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        header_frame.pack(fill="x", padx=16, pady=(16, 8))

        chat_title = ctk.CTkLabel(
            header_frame,
            text="Chat",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#1a1a1a"
        )
        chat_title.pack(side="left")

        # Кнопка нового чата
        new_chat_btn = ctk.CTkButton(
            header_frame,
            text="+",
            width=30,
            height=30,
            font=ctk.CTkFont(size=20),
            fg_color="transparent",
            text_color="#0084ff",
            hover_color=self.hover_color,
            corner_radius=15,
            command=self.new_chat
        )
        new_chat_btn.pack(side="right")

        # Поле поиска
        self.search_entry = ctk.CTkEntry(
            self.sidebar,
            placeholder_text="🔍 Поиск",
            height=40,
            font=ctk.CTkFont(size=13),
            fg_color="#f0f2f5",
            text_color="#1a1a1a",
            corner_radius=20
        )
        self.search_entry.pack(fill="x", padx=16, pady=(0, 12))

        # Заголовок "Last chats"
        last_chats_label = ctk.CTkLabel(
            self.sidebar,
            text="Last chats",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#1a1a1a"
        )
        last_chats_label.pack(anchor="w", padx=16, pady=(0, 8))

        # Скроллируемый фрейм для чатов
        self.chats_scroll = ctk.CTkScrollableFrame(
            self.sidebar,
            fg_color="transparent",
            scrollbar_button_color="#c1c1c1",
            scrollbar_button_hover_color="#a1a1a1"
        )
        self.chats_scroll.pack(fill="both", expand=True, padx=8)

        # Данные чатов
        self.chats = [
            {
                "name": "Real estate deals",
                "status": "typing...",
                "time": "11:15",
                "unread": False,
                "avatar": "🏠",
                "messages": [
                    {"sender": "Kate Johnson",
                     "text": "Recently I saw properties in a great location that I did not pay attention to before 😊",
                     "time": "11:24", "is_user": False},
                    {"sender": "Evan Scott", "text": "Ooo, why don't you say something more", "time": "11:25",
                     "is_user": False},
                    {"sender": "Evan Scott", "text": "@Robert ? 😉", "time": "11:25", "is_user": False},
                    {"sender": "You", "text": "He creates an atmosphere of mystery 😉", "time": "11:26", "is_user": True}
                ]
            },
            {
                "name": "Kate Johnson",
                "status": "I will send the document s...",
                "time": "11:15",
                "unread": False,
                "avatar": "KJ",
                "messages": [
                    {"sender": "You", "text": "Hi Kate! How are you?", "time": "10:30", "is_user": True},
                    {"sender": "Kate Johnson", "text": "Hello! I'm doing great, thanks! Just finished the project",
                     "time": "10:31", "is_user": False},
                    {"sender": "You", "text": "That's awesome! Can you share the documents?", "time": "10:32",
                     "is_user": True},
                    {"sender": "Kate Johnson", "text": "Sure, I'll send them right away", "time": "10:33",
                     "is_user": False}
                ]
            },
            {
                "name": "Tamara Shevchenko",
                "status": "are you going to a busine...",
                "time": "10:05",
                "unread": False,
                "avatar": "TS",
                "messages": [
                    {"sender": "Tamara Shevchenko", "text": "Are you going to the business conference tomorrow?",
                     "time": "10:05", "is_user": False},
                    {"sender": "You", "text": "Yes, I'll be there! See you tomorrow", "time": "10:06", "is_user": True}
                ]
            },
            {
                "name": "Joshua Clarkson",
                "status": "I suggest to start, I have n...",
                "time": "15.09",
                "unread": False,
                "avatar": "JC",
                "messages": [
                    {"sender": "Joshua Clarkson", "text": "I suggest to start, I have new ideas for the project",
                     "time": "15:09", "is_user": False},
                    {"sender": "You", "text": "Great! Let's schedule a meeting", "time": "15:10", "is_user": True}
                ]
            },
            {
                "name": "Jeroen Zoet",
                "status": "We need to start a new re...",
                "time": "14.09",
                "unread": False,
                "avatar": "JZ",
                "messages": [
                    {"sender": "Jeroen Zoet", "text": "We need to start a new research project", "time": "14:09",
                     "is_user": False},
                    {"sender": "You", "text": "Sounds interesting! Let's discuss details", "time": "14:10",
                     "is_user": True}
                ]
            }
        ]

        # Создаем виджеты чатов
        self.chat_widgets = []
        for i, chat in enumerate(self.chats):
            self.add_chat_item(chat, i)

    def add_chat_item(self, chat, index):
        """Добавление элемента чата"""
        # Контейнер для чата
        chat_frame = ctk.CTkFrame(
            self.chats_scroll,
            fg_color="transparent",
            corner_radius=10,
            height=70
        )
        chat_frame.pack(fill="x", pady=2)
        chat_frame.pack_propagate(False)

        # Привязываем события
        chat_frame.bind('<Enter>', lambda e, f=chat_frame: self.on_chat_hover_enter(f))
        chat_frame.bind('<Leave>', lambda e, f=chat_frame: self.on_chat_hover_leave(f))
        chat_frame.bind('<Button-1>', lambda e, i=index: self.select_chat(i))

        # Аватар
        avatar_frame = ctk.CTkFrame(
            chat_frame,
            width=50,
            height=50,
            fg_color="#e4e6eb",
            corner_radius=25
        )
        avatar_frame.pack(side="left", padx=(8, 12), pady=10)
        avatar_frame.pack_propagate(False)

        avatar_label = ctk.CTkLabel(
            avatar_frame,
            text=chat["avatar"],
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#1a1a1a"
        )
        avatar_label.pack(expand=True)

        # Информация о чате
        info_frame = ctk.CTkFrame(chat_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, pady=10)

        name_label = ctk.CTkLabel(
            info_frame,
            text=chat["name"],
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#1a1a1a",
            anchor="w"
        )
        name_label.pack(anchor="w")

        status_label = ctk.CTkLabel(
            info_frame,
            text=chat["status"],
            font=ctk.CTkFont(size=11),
            text_color="#65676b",
            anchor="w"
        )
        status_label.pack(anchor="w")

        # Время
        time_label = ctk.CTkLabel(
            chat_frame,
            text=chat["time"],
            font=ctk.CTkFont(size=10),
            text_color="#65676b"
        )
        time_label.pack(side="right", padx=12)

        # Сохраняем ссылки
        chat_frame.index = index
        chat_frame.name = chat["name"]

    def on_chat_hover_enter(self, frame):
        """Эффект при наведении"""
        if not hasattr(frame, 'selected') or not frame.selected:
            frame.configure(fg_color=self.hover_color)

    def on_chat_hover_leave(self, frame):
        """Снятие эффекта"""
        if not hasattr(frame, 'selected') or not frame.selected:
            frame.configure(fg_color="transparent")

    def select_chat(self, index):
        """Выбор чата"""
        # Обновляем выделение
        for i, widget in enumerate(self.chats_scroll.winfo_children()):
            if hasattr(widget, 'selected'):
                delattr(widget, 'selected')
                widget.configure(fg_color="transparent")

        selected_widget = self.chats_scroll.winfo_children()[index]
        selected_widget.selected = True
        selected_widget.configure(fg_color=self.hover_color)

        # Обновляем заголовок и участников
        chat = self.chats[index]
        self.chat_header_label.configure(text=chat["name"])

        # Обновляем список участников
        if index == 0:
            members_text = "Kate Johnson, Evan Scott, Robert"
        else:
            members_text = chat["name"]
        self.members_label.configure(text=members_text)

        # Загружаем сообщения
        self.load_chat_messages(index)

    def create_chat_area(self):
        """Создание области чата"""
        self.chat_area = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.chat_bg,
            corner_radius=0
        )
        self.chat_area.pack(side="right", fill="both", expand=True)

        # Заголовок чата
        header_frame = ctk.CTkFrame(
            self.chat_area,
            fg_color="transparent",
            height=70,
            border_width=0,
            border_spacing=0
        )
        header_frame.pack(fill="x", padx=20, pady=(15, 0))
        header_frame.pack_propagate(False)

        self.chat_header_label = ctk.CTkLabel(
            header_frame,
            text="Real estate deals",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#1a1a1a"
        )
        self.chat_header_label.pack(side="left")

        self.members_label = ctk.CTkLabel(
            header_frame,
            text="Kate Johnson, Evan Scott, Robert",
            font=ctk.CTkFont(size=12),
            text_color="#65676b"
        )
        self.members_label.pack(side="left", padx=(10, 0))

        # Разделитель
        separator = ctk.CTkFrame(
            self.chat_area,
            height=1,
            fg_color="#e4e6eb"
        )
        separator.pack(fill="x", padx=20, pady=(10, 0))

        # Область сообщений
        self.messages_frame = ctk.CTkScrollableFrame(
            self.chat_area,
            fg_color="transparent",
            scrollbar_button_color="#c1c1c1"
        )
        self.messages_frame.pack(fill="both", expand=True, padx=20, pady=(15, 10))

        # Индикатор печатания
        typing_frame = ctk.CTkFrame(self.chat_area, fg_color="transparent", height=30)
        typing_frame.pack(fill="x", padx=20)
        typing_frame.pack_propagate(False)

        self.typing_label = ctk.CTkLabel(
            typing_frame,
            text="Robert is typing...",
            font=ctk.CTkFont(size=11, slant="italic"),
            text_color="#65676b"
        )
        self.typing_label.pack(anchor="w")

        # Область ввода сообщения
        input_frame = ctk.CTkFrame(self.chat_area, fg_color="transparent", height=80)
        input_frame.pack(fill="x", padx=20, pady=(0, 20))
        input_frame.pack_propagate(False)

        # Контейнер для поля ввода
        input_container = ctk.CTkFrame(
            input_frame,
            fg_color="#f0f2f5",
            corner_radius=20,
            border_width=1,
            border_color="#e4e6eb"
        )
        input_container.pack(fill="both", expand=True)

        self.message_entry = ctk.CTkTextbox(
            input_container,
            height=50,
            font=ctk.CTkFont(size=13),
            fg_color="#f0f2f5",
            text_color="#1a1a1a",
            corner_radius=20,
            wrap="word"
        )
        self.message_entry.pack(side="left", fill="both", expand=True, padx=12, pady=8)

        # Кнопка отправки
        send_button = ctk.CTkButton(
            input_container,
            text="➤",
            width=40,
            height=40,
            font=ctk.CTkFont(size=20),
            fg_color="transparent",
            text_color="#0084ff",
            hover_color="#e4e6eb",
            corner_radius=20,
            command=self.send_message
        )
        send_button.pack(side="right", padx=8)

        # Привязка клавиш
        self.message_entry.bind('<Control-Return>', self.send_message)

    def load_chat_messages(self, index):
        """Загрузка сообщений для выбранного чата"""
        # Очищаем область сообщений
        for widget in self.messages_frame.winfo_children():
            widget.destroy()

        # Загружаем сообщения
        chat = self.chats[index]
        for msg in chat["messages"]:
            self.add_message(msg["sender"], msg["text"], msg["time"], msg["is_user"])

    def add_message(self, sender, text, time, is_user=False):
        """Добавление сообщения в чат"""
        # Контейнер для сообщения
        msg_container = ctk.CTkFrame(
            self.messages_frame,
            fg_color="transparent"
        )
        msg_container.pack(fill="x", pady=(0, 12))

        if is_user:
            # Свое сообщение (справа)
            msg_frame = ctk.CTkFrame(
                msg_container,
                fg_color=self.user_msg_bg,
                corner_radius=12
            )
            msg_frame.pack(side="right", padx=(50, 0))

            # Текст сообщения
            msg_text = ctk.CTkLabel(
                msg_frame,
                text=text,
                font=ctk.CTkFont(size=13),
                text_color="#1a1a1a",
                wraplength=400,
                justify="right"
            )
            msg_text.pack(padx=12, pady=(8, 4))

            # Время
            time_label = ctk.CTkLabel(
                msg_frame,
                text=time,
                font=ctk.CTkFont(size=10),
                text_color="#65676b"
            )
            time_label.pack(anchor="e", padx=12, pady=(0, 8))

        else:
            # Чужое сообщение (слева)
            # Имя отправителя
            name_label = ctk.CTkLabel(
                msg_container,
                text=sender,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#1a1a1a"
            )
            name_label.pack(anchor="w", padx=(0, 0), pady=(0, 2))

            msg_frame = ctk.CTkFrame(
                msg_container,
                fg_color=self.other_msg_bg,
                corner_radius=12
            )
            msg_frame.pack(side="left", padx=(0, 50))

            # Текст сообщения
            msg_text = ctk.CTkLabel(
                msg_frame,
                text=text,
                font=ctk.CTkFont(size=13),
                text_color="#1a1a1a",
                wraplength=400,
                justify="left"
            )
            msg_text.pack(padx=12, pady=(8, 4))

            # Время
            time_label = ctk.CTkLabel(
                msg_frame,
                text=time,
                font=ctk.CTkFont(size=10),
                text_color="#65676b"
            )
            time_label.pack(anchor="w", padx=12, pady=(0, 8))

    def send_message(self, event=None):
        """Отправка сообщения"""
        message = self.message_entry.get("1.0", "end-1c").strip()

        if message:
            current_time = datetime.now().strftime("%H:%M")
            current_chat = self.get_current_chat()

            if current_chat is not None:
                # Добавляем сообщение в данные
                current_chat["messages"].append({
                    "sender": "You",
                    "text": message,
                    "time": current_time,
                    "is_user": True
                })

                # Обновляем статус чата
                current_chat["status"] = message[:30] + "..." if len(message) > 30 else message
                current_chat["time"] = current_time

                # Добавляем сообщение в интерфейс
                self.add_message("You", message, current_time, True)

                # Очищаем поле ввода
                self.message_entry.delete("1.0", "end")

                # Обновляем список чатов
                self.update_chat_list()

    def get_current_chat(self):
        """Получение текущего чата"""
        current_name = self.chat_header_label.cget("text")
        for chat in self.chats:
            if chat["name"] == current_name:
                return chat
        return None

    def update_chat_list(self):
        """Обновление списка чатов"""
        # Очищаем список
        for widget in self.chats_scroll.winfo_children():
            widget.destroy()

        # Пересоздаем чаты
        for i, chat in enumerate(self.chats):
            self.add_chat_item(chat, i)

    def animate_typing(self):
        """Анимация статуса печатания"""
        dots = 0

        def update_typing():
            nonlocal dots
            dots = (dots + 1) % 4
            text = "Robert is typing" + "." * dots
            self.typing_label.configure(text=text)
            self.root.after(500, update_typing)

        update_typing()

    def new_chat(self):
        """Создание нового чата"""
        # Создаем диалоговое окно
        dialog = ctk.CTkInputDialog(
            text="Enter chat name:",
            title="New Chat"
        )
        chat_name = dialog.get_input()

        if chat_name:
            # Добавляем новый чат
            new_chat = {
                "name": chat_name,
                "status": "No messages yet",
                "time": "Now",
                "unread": False,
                "avatar": chat_name[0].upper(),
                "messages": []
            }
            self.chats.append(new_chat)
            self.update_chat_list()

    def run(self):
        """Запуск приложения"""
        self.root.mainloop()


def main():
    app = ModernMessenger()
    app.run()


if __name__ == "__main__":
    main()