import customtkinter as ctk
import tkinter as tk
from datetime import datetime

# Настройка темы
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class SimpleMessenger:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Мессенджер")
        self.root.geometry("1000x700")
        self.root.minsize(1000, 700)

        # Светлая цветовая схема
        self.bg_color = "#f8f9fa"
        self.card_color = "#ffffff"
        self.border_color = "#e9ecef"
        self.text_primary = "#212529"
        self.text_secondary = "#868e96"
        self.message_bg = "#f1f3f5"

        # Создание интерфейса
        self.setup_ui()

        # Добавляем пример данных
        self.add_example_data()

    def setup_ui(self):
        """Настройка основного интерфейса"""
        # Создание меню (должно быть до остальных элементов)
        self.create_menu()

        # Основной контейнер
        self.main_container = ctk.CTkFrame(
            self.root,
            fg_color=self.bg_color
        )
        self.main_container.pack(fill="both", expand=True)

        # Контентная область
        self.content_frame = ctk.CTkFrame(
            self.main_container,
            fg_color=self.bg_color
        )
        self.content_frame.pack(fill="both", expand=True, padx=1, pady=1)

        # Две колонки
        self.sidebar = ctk.CTkFrame(
            self.content_frame,
            width=280,
            fg_color=self.card_color,
            corner_radius=0
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.chat_area = ctk.CTkFrame(
            self.content_frame,
            fg_color=self.bg_color,
            corner_radius=0
        )
        self.chat_area.pack(side="right", fill="both", expand=True)

        # Заполнение интерфейса
        self.create_sidebar()
        self.create_chat_area()

    def create_menu(self):
        """Создание верхнего меню"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Новый чат", command=self.new_chat)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)

        # Меню "Правка"
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Правка", menu=edit_menu)
        edit_menu.add_command(label="Настройки", command=self.settings)

        # Меню "Помощь"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Помощь", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.about)

    def create_sidebar(self):
        """Создание боковой панели"""
        # Заголовок
        header = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=70)
        header.pack(fill="x", padx=20, pady=(20, 10))
        header.pack_propagate(False)

        title = ctk.CTkLabel(
            header,
            text="Чаты",
            font=ctk.CTkFont(size=20, weight="normal"),
            text_color=self.text_primary
        )
        title.pack(side="left")

        # Поиск
        self.search = ctk.CTkEntry(
            self.sidebar,
            placeholder_text="Поиск",
            height=36,
            font=ctk.CTkFont(size=13),
            fg_color=self.bg_color,
            text_color=self.text_primary,
            corner_radius=8,
            border_width=0
        )
        self.search.pack(fill="x", padx=20, pady=(0, 20))

        # Список чатов
        self.chats_frame = ctk.CTkScrollableFrame(
            self.sidebar,
            fg_color="transparent",
            scrollbar_button_color="#dee2e6"
        )
        self.chats_frame.pack(fill="both", expand=True, padx=12)

        # Данные чатов
        self.chats_data = [
            {"name": "Кейт Джонсон", "preview": "Я отправлю документ...", "time": "11:15"},
            {"name": "Недвижимость", "preview": "печатает...", "time": "11:15"},
            {"name": "Тамара Шевченко", "preview": "ты собираешься на деловую...", "time": "10:05"},
            {"name": "Джошуа Кларксон", "preview": "Предлагаю начать, у меня...", "time": "15.09"},
            {"name": "Йерун Зут", "preview": "Нам нужно начать новый...", "time": "14.09"},
            {"name": "Кейт Джонсон", "preview": "Я отправлю документ...", "time": "11:15"},
            {"name": "Недвижимость", "preview": "печатает...", "time": "11:15"},
            {"name": "Тамара Шевченко", "preview": "ты собираешься на деловую...", "time": "10:05"},
            {"name": "Джошуа Кларксон", "preview": "Предлагаю начать, у меня...", "time": "15.09"},
            {"name": "Йерун Зут", "preview": "Нам нужно начать новый...", "time": "14.09"},
            {"name": "Кейт Джонсон", "preview": "Я отправлю документ...", "time": "11:15"},
            {"name": "Недвижимость", "preview": "печатает...", "time": "11:15"},
            {"name": "Тамара Шевченко", "preview": "ты собираешься на деловую...", "time": "10:05"},
            {"name": "Джошуа Кларксон", "preview": "Предлагаю начать, у меня...", "time": "15.09"},
            {"name": "Йерун Зут", "preview": "Нам нужно начать новый...", "time": "14.09"}
        ]

        # Создаем элементы чатов
        self.chat_items = []
        for i, chat in enumerate(self.chats_data):
            self.add_chat_item(chat, i)

    def add_chat_item(self, chat, index):
        """Добавление элемента чата"""
        # Контейнер чата
        chat_item = ctk.CTkFrame(
            self.chats_frame,
            fg_color="transparent",
            height=65,
            corner_radius=8
        )
        chat_item.pack(fill="x", pady=2)
        chat_item.pack_propagate(False)

        # Информация
        info_frame = ctk.CTkFrame(chat_item, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=12, pady=8)

        name = ctk.CTkLabel(
            info_frame,
            text=chat["name"],
            font=ctk.CTkFont(size=14, weight="normal"),
            text_color=self.text_primary,
            anchor="w"
        )
        name.pack(anchor="w")

        preview = ctk.CTkLabel(
            info_frame,
            text=chat["preview"],
            font=ctk.CTkFont(size=12),
            text_color=self.text_secondary,
            anchor="w"
        )
        preview.pack(anchor="w", pady=(2, 0))

        # Время
        time = ctk.CTkLabel(
            chat_item,
            text=chat["time"],
            font=ctk.CTkFont(size=11),
            text_color=self.text_secondary
        )
        time.pack(side="right", padx=12)

        # Сохраняем ссылку
        chat_item.index = index
        chat_item.bind("<Button-1>", lambda e, i=index: self.select_chat(i))

        self.chat_items.append(chat_item)

    def create_chat_area(self):
        """Создание области чата"""
        # Заголовок чата
        header = ctk.CTkFrame(self.chat_area, fg_color="transparent", height=70)
        header.pack(fill="x", padx=24, pady=(20, 0))
        header.pack_propagate(False)

        self.chat_title = ctk.CTkLabel(
            header,
            text="Кейт Джонсон",
            font=ctk.CTkFont(size=18, weight="normal"),
            text_color=self.text_primary
        )
        self.chat_title.pack(side="left")

        # Область сообщений
        self.messages_frame = ctk.CTkScrollableFrame(
            self.chat_area,
            fg_color="transparent",
            scrollbar_button_color="#dee2e6"
        )
        self.messages_frame.pack(fill="both", expand=True, padx=24, pady=(16, 12))

        # Поле ввода (горизонтальная компоновка)
        input_container = ctk.CTkFrame(self.chat_area, fg_color="transparent", height=60)
        input_container.pack(fill="x", padx=24, pady=(0, 20))
        input_container.pack_propagate(False)

        # Создаем горизонтальный фрейм
        input_row = ctk.CTkFrame(input_container, fg_color="transparent")
        input_row.pack(fill="both", expand=True)

        # Поле ввода текста
        self.message_input = ctk.CTkTextbox(
            input_row,
            height=50,
            font=ctk.CTkFont(size=13),
            fg_color=self.card_color,
            text_color=self.text_primary,
            corner_radius=12,
            border_width=1,
            border_color=self.border_color
        )
        self.message_input.pack(side="left", fill="both", expand=True)

        # Кнопка отправки
        send_btn = ctk.CTkButton(
            input_row,
            text="Отправить",
            width=90,
            height=50,
            font=ctk.CTkFont(size=13),
            fg_color=self.bg_color,
            text_color=self.text_primary,
            hover_color=self.border_color,
            corner_radius=12,
            border_width=1,
            border_color=self.border_color,
            command=self.send_message
        )
        send_btn.pack(side="right", padx=(12, 0))

        # Привязка клавиш
        self.message_input.bind("<Command-Return>", self.send_message)
        self.message_input.bind("<Control-Return>", self.send_message)

    def select_chat(self, index):
        """Выбор чата"""
        chat = self.chats_data[index]
        self.chat_title.configure(text=chat["name"])

        # Очищаем сообщения
        for widget in self.messages_frame.winfo_children():
            widget.destroy()

        # Загружаем пример сообщений
        if index == 0:  # Кейт Джонсон
            self.add_message("Кейт Джонсон", "Привет! Как дела?", "10:30")
            self.add_message("Вы", "Хорошо, спасибо! А у тебя?", "10:31", is_user=True)
            self.add_message("Кейт Джонсон", "Я скоро отправлю документ", "11:15")
            self.add_message("Кейт Джонсон", "Недавно я увидела отличную недвижимость в хорошем месте", "11:24")
            self.add_message("Кейт Джонсон", "Ого, расскажи подробнее", "11:25")
            self.add_message("Вы", "Он создает атмосферу загадочности 😉", "11:26", is_user=True)
            self.add_message("Кейт Джонсон", "печатает...", "11:27")
            self.add_message("Кейт Джонсон", "Ты собираешься на деловую встречу завтра?", "10:05")
            self.add_message("Вы", "Да, буду там. Увидимся!", "10:06", is_user=True)
            self.add_message("Кейт Джонсон", "Предлагаю начать, у меня есть новые идеи для проекта", "15:09")
            self.add_message("Вы", "Отлично! Давай обсудим", "15:10", is_user=True)
        elif index == 1:  # Недвижимость
            self.add_message("Кейт Джонсон", "Недавно я увидела отличную недвижимость в хорошем месте", "11:24")
            self.add_message("Кейт Джонсон", "Ого, расскажи подробнее", "11:25")
            self.add_message("Вы", "Он создает атмосферу загадочности 😉", "11:26", is_user=True)
            self.add_message("Кейт Джонсон", "печатает...", "11:27")
        elif index == 2:  # Тамара Шевченко
            self.add_message("Тамара Шевченко", "Ты собираешься на деловую встречу завтра?", "10:05")
            self.add_message("Вы", "Да, буду там. Увидимся!", "10:06", is_user=True)
        elif index == 3:  # Джошуа Кларксон
            self.add_message("Джошуа Кларксон", "Предлагаю начать, у меня есть новые идеи для проекта", "15:09")
            self.add_message("Вы", "Отлично! Давай обсудим", "15:10", is_user=True)
        else:  # Йерун Зут
            self.add_message("Йерун Зут", "Нам нужно начать новый исследовательский проект", "14:09")
            self.add_message("Вы", "Звучит интересно! Давай обсудим детали", "14:10", is_user=True)

    def add_message(self, sender, text, time, is_user=False):
        """Добавление сообщения"""
        msg_container = ctk.CTkFrame(self.messages_frame, fg_color="transparent")
        msg_container.pack(fill="x", pady=(0, 16))

        if is_user:
            # Свое сообщение
            msg_frame = ctk.CTkFrame(
                msg_container,
                fg_color=self.message_bg,
                corner_radius=12
            )
            msg_frame.pack(side="right", padx=(40, 0))

            msg_text = ctk.CTkLabel(
                msg_frame,
                text=text,
                font=ctk.CTkFont(size=13),
                text_color=self.text_primary,
                wraplength=350,
                justify="right"
            )
            msg_text.pack(padx=12, pady=(8, 4))

            time_label = ctk.CTkLabel(
                msg_frame,
                text=time,
                font=ctk.CTkFont(size=10),
                text_color=self.text_secondary
            )
            time_label.pack(anchor="e", padx=12, pady=(0, 6))
        else:
            # Чужое сообщение
            name_label = ctk.CTkLabel(
                msg_container,
                text=sender,
                font=ctk.CTkFont(size=12, weight="normal"),
                text_color=self.text_secondary
            )
            name_label.pack(anchor="w", pady=(0, 2))

            msg_frame = ctk.CTkFrame(
                msg_container,
                fg_color=self.message_bg,
                corner_radius=12
            )
            msg_frame.pack(side="left", padx=(0, 40))

            msg_text = ctk.CTkLabel(
                msg_frame,
                text=text,
                font=ctk.CTkFont(size=13),
                text_color=self.text_primary,
                wraplength=350,
                justify="left"
            )
            msg_text.pack(padx=12, pady=(8, 4))

            time_label = ctk.CTkLabel(
                msg_frame,
                text=time,
                font=ctk.CTkFont(size=10),
                text_color=self.text_secondary
            )
            time_label.pack(anchor="w", padx=12, pady=(0, 6))

    def send_message(self, event=None):
        """Отправка сообщения"""
        message = self.message_input.get("1.0", "end-1c").strip()

        if message:
            current_time = datetime.now().strftime("%H:%M")
            self.add_message("Вы", message, current_time, is_user=True)
            self.message_input.delete("1.0", "end")

    def add_example_data(self):
        """Добавление примера сообщений"""
        self.add_message("Кейт Джонсон", "Привет! Как дела?", "10:30")
        self.add_message("Вы", "Хорошо, спасибо! А у тебя?", "10:31", is_user=True)
        self.add_message("Кейт Джонсон", "Я скоро отправлю документ", "11:15")

    def new_chat(self):
        """Создание нового чата"""
        # Создаем диалог для ввода имени чата
        dialog = ctk.CTkInputDialog(
            text="Введите название чата:",
            title="Новый чат"
        )
        chat_name = dialog.get_input()

        if chat_name:
            # Добавляем новый чат
            new_chat = {
                "name": chat_name,
                "preview": "Нет сообщений",
                "time": "только что"
            }
            self.chats_data.append(new_chat)
            self.add_chat_item(new_chat, len(self.chats_data) - 1)

    def settings(self):
        """Настройки"""
        settings_window = ctk.CTkToplevel(self.root)
        settings_window.title("Настройки")
        settings_window.geometry("400x300")
        settings_window.grab_set()

        label = ctk.CTkLabel(
            settings_window,
            text="Настройки приложения",
            font=ctk.CTkFont(size=16),
            text_color=self.text_primary
        )
        label.pack(pady=50)

        close_btn = ctk.CTkButton(
            settings_window,
            text="Закрыть",
            command=settings_window.destroy,
            fg_color=self.bg_color,
            text_color=self.text_primary,
            hover_color=self.border_color
        )
        close_btn.pack(pady=20)

    def about(self):
        """О программе"""
        about_window = ctk.CTkToplevel(self.root)
        about_window.title("О программе")
        about_window.geometry("400x250")
        about_window.grab_set()

        about_text = """
        Мессенджер

        Версия: 1.0.0
        Простой и удобный мессенджер

        © 2024
        """

        label = ctk.CTkLabel(
            about_window,
            text=about_text,
            font=ctk.CTkFont(size=12),
            text_color=self.text_primary,
            justify="center"
        )
        label.pack(expand=True)

        close_btn = ctk.CTkButton(
            about_window,
            text="Закрыть",
            command=about_window.destroy,
            fg_color=self.bg_color,
            text_color=self.text_primary,
            hover_color=self.border_color
        )
        close_btn.pack(pady=20)

    def run(self):
        """Запуск приложения"""
        self.root.mainloop()


if __name__ == "__main__":
    app = SimpleMessenger()
    app.run()