import subprocess
import platform


def authenticate_with_domain(username, password):
    """
    Проверка учетных данных через домен Windows
    """
    # Если система Windows
    if platform.system() == 'Windows':
        try:
            # Используем net use для проверки (работает без монтирования диска)
            cmd = f'net use \\\\giap.org\\IPC$ /user:{username} {password}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            # Если успешно, команда вернет код 0
            if result.returncode == 0:
                # Получаем полное имя пользователя и отдел
                print("OK", username, password)
                user_info = get_user_info_from_domain(username)
                return True, user_info
            else:
                return False, None
        except Exception as e:
            print(f"Ошибка аутентификации: {e}")
            return False, None
    else:
        # Для Linux/Mac (заглушка)
        print("Доменная аутентификация доступна только на Windows")
        # Временно разрешаем любые учетные данные для тестирования
        return True, {
            'full_name': username,
            'department': 'Test Department'
        }


def get_user_info_from_domain(username):
    """
    Получение информации о пользователе из Active Directory
    Требуется установка: pip install ldap3
    """
    try:
        from ldap3 import Server, Connection, ALL

        # Настройки вашего домена (нужно заменить на реальные)
        server = Server('giap.org', get_info=ALL)
        conn = Connection(server, user=f'{username}@giap.org', auto_bind=True)

        # Поиск информации о пользователе
        conn.search('dc=domain,dc=com',
                    f'(sAMAccountName={username})',
                    attributes=['displayName', 'department'])

        if conn.entries:
            return {
                'full_name': str(conn.entries[0].displayName),
                'department': str(conn.entries[0].department)
            }
    except:
        # Если не получилось, возвращаем заглушку
        pass

    return {
        'full_name': username,
        'department': 'Unknown'
    }

authenticate_with_domain(username = "oavp_14", password = "EW.a=8*2T9")