import socket
import getpass
import subprocess


def get_user_with_ad_name():
    """
    Получение имени пользователя и полного имени из AD
    """
    username = getpass.getuser()

    # Получаем IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
    except:
        ip_address = socket.gethostbyname(socket.gethostname())

    # Получаем полное имя из AD
    full_name = "Не удалось получить"
    try:
        # Запрашиваем информацию о пользователе в домене
        result = subprocess.run(['net', 'user', username, '/domain'],
                                capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            # Парсим вывод net user
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Full Name' in line or 'Полное имя' in line:
                    # Извлекаем значение после двоеточия
                    parts = line.split(':')
                    if len(parts) > 1:
                        full_name = parts[1].strip()
                    break
    except Exception as e:
        full_name = f"Ошибка: {str(e)}"

    # Выводим результат
    print("=" * 50)
    print(f"Логин: {username}")
    print(f"Полное имя: {full_name}")
    print(f"IP-адрес: {ip_address}")
    print("=" * 50)


# Запуск
if __name__ == "__main__":
    get_user_with_ad_name()