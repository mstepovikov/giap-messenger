# giap-messenger
A corporate messenger project with basic functionality. FastAPI+Tkinter

# Installing libraries
pip install fastapi uvicorn websockets websocket-client requests ldap3

# Project structure
giap-messenger/
    server/
        main.py           # Основной файл сервера
        database.py       # Работа с базой данных
        auth.py           # Аутентификация (доменная)
        users.db          # Файл базы данных (создастся сам)
    client/
        main.py           # Основной файл клиента
        config.py         # Настройки (адрес сервера)
