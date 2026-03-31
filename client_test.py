import tkinter as tk
from tkinter import scrolledtext
import threading
import websocket
from websocket._exceptions import WebSocketConnectionClosedException


class SimpleChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Тестовый клиент")
        self.root.geometry("500x400")
        self.ws = None
        self.connected = False

        # Поле для сообщений
        self.text_area = scrolledtext.ScrolledText(root, height=15)
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Поле ввода
        self.entry = tk.Entry(root)
        self.entry.pack(fill=tk.X, padx=10, pady=5)
        self.entry.bind("<Return>", self.send_message)

        # Кнопка
        self.send_button = tk.Button(root, text="Отправить", command=self.send_message)
        self.send_button.pack(pady=5)

        # Статус
        self.status_label = tk.Label(root, text="Подключение...", fg="orange")
        self.status_label.pack(pady=2)

        # Запускаем WebSocket в отдельном потоке
        self.ws_thread = threading.Thread(target=self.connect_websocket, daemon=True)
        self.ws_thread.start()

        # Обработка закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def connect_websocket(self):
        def on_message(ws, message):
            self.root.after(0, self.add_message, f"Сервер: {message}")

        def on_open(ws):
            self.root.after(0, self.update_status, "Подключено", "green")
            self.connected = True

        def on_close(ws, close_status_code, close_msg):
            self.root.after(0, self.update_status, "Отключено", "red")
            self.connected = False

        def on_error(ws, error):
            self.root.after(0, self.update_status, f"Ошибка: {error}", "red")
            self.connected = False

        self.ws = websocket.WebSocketApp("ws://localhost:8000/ws",
                                         on_message=on_message,
                                         on_open=on_open,
                                         on_close=on_close,
                                         on_error=on_error)

        try:
            self.ws.run_forever()
        except Exception as e:
            self.root.after(0, self.update_status, f"Ошибка подключения: {e}", "red")

    def update_status(self, text, color):
        self.status_label.config(text=text, fg=color)
        self.send_button.config(state="normal" if self.connected else "disabled")
        self.entry.config(state="normal" if self.connected else "disabled")

    def add_message(self, message):
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.see(tk.END)

    def send_message(self, event=None):
        if not self.connected or not self.ws:
            self.add_message("Ошибка: Нет подключения к серверу")
            return

        message = self.entry.get()
        if message:
            try:
                self.ws.send(message)
                self.add_message(f"Я: {message}")
                self.entry.delete(0, tk.END)
            except WebSocketConnectionClosedException:
                self.add_message("Ошибка: Соединение закрыто")
                self.update_status("Отключено", "red")
            except Exception as e:
                self.add_message(f"Ошибка отправки: {e}")

    def on_closing(self):
        """Корректное закрытие соединения при выходе"""
        if self.ws:
            try:
                self.ws.close()
            except:
                pass
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleChatClient(root)
    root.mainloop()