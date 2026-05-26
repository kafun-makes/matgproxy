import asyncio
import os
import secrets
import subprocess
import sys
import time
import urllib.request

# Файл настроек в папке со скриптом
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "tg_config_win.txt")
# Файлы для фонового запуска
VBS_RUNNER = os.path.join(BASE_DIR, "tg_proxy_hidden.vbs")
BAT_RUNNER = os.path.join(BASE_DIR, "tg_proxy_start.bat")

PORT = 2834
USER = "tg_user"
PASSWORD = secrets.token_hex(8)
LANG = "ru"

STRINGS = {
    "ru": {
        "title": "         УПРАВЛЕНИЕ ТЕЛЕГРАМ ПРОКСИ ДЛЯ WINDOWS        ",
        "status": " Текущий статус прокси: ",
        "active": "РАБОТАЕТ В ФОНЕ (ПОРТ: {})",
        "inactive": "ОСТАНОВЛЕН",
        "login": " Текущий Логин:  {}",
        "pass": " Текущий Пароль: {}",
        "opt1": " 1. Показать ссылку для подключения в Telegram",
        "opt2": " 2. Изменить ПОРТ прокси",
        "opt3": " 3. Изменить ЛОГИН",
        "opt4": " 4. Изменить ПАРОЛЬ",
        "opt5": " 5. Сгенерировать новый случайный пароль",
        "opt6": " 6. Запустить / Перезапустить прокси в фоне",
        "opt7": " 7. Остановить фоновый прокси",
        "opt8": " 8. Тест скорости и пинга",
        "opt9": " 9. ПОЛНОЕ УДАЛЕНИЕ СИСТЕМНЫХ ХВОСТОВ",
        "opt0": " 0. Выйти из меню",
        "choice": "Выберите действие (0-9): ",
        "link_title": "\n Ссылка для Telegram:",
        "press_enter": "\nНажмите Enter для возврата в меню...",
        "enter_port": "\nВведите новый порт (сейчас {}): ",
        "port_changed": " Порт изменен. Перезапустите прокси (пункт 6).",
        "enter_login": "\nВведите новый логин (сейчас {}): ",
        "login_changed": " Логин изменен.",
        "enter_pass": "\nВведите новый пароль (сейчас {}): ",
        "pass_changed": " Пароль изменен.",
        "new_pass_gen": " Сгенерирован новый пароль: {}",
        "restarting": "\n Запуск фонового процесса в Windows...",
        "restarted": " Прокси успешно запущен в фоне!",
        "stopping": "\n Остановка фонового процесса...",
        "stopped": " Фоновый прокси остановлен.",
        "testing": "\nТестирование скорости соединения...",
        "test_res": " Результаты теста:\n   - Пинг: {:.1f} мс\n   - Скорость скачивания: {:.2f} Мбит/с",
        "test_fail": " Ошибка теста: Серверы недоступны.",
        "uninstalling": "\nУдаление команды matg и конфигураций из Windows...",
        "uninstalled": "Скрипт вычищен из системы.",
        "init_done": "\n Настройка Windows завершена! Команда 'matg' зарегистрирована.",
    },
    "en": {
        "title": "         TELEGRAM PROXY MANAGEMENT FOR WINDOWS        ",
        "status": " Current proxy status: ",
        "active": "RUNNING IN BACKGROUND (PORT: {})",
        "inactive": "STOPPED",
        "login": " Current Username: {}",
        "pass": " Current Password: {}",
        "opt1": " 1. Show Telegram connection link",
        "opt2": " 2. Change proxy PORT",
        "opt3": " 3. Change USERNAME",
        "opt4": " 4. Change PASSWORD",
        "opt5": " 5. Generate new random password",
        "opt6": " 6. Start / Restart proxy in background",
        "opt7": " 7. Stop background proxy",
        "opt8": " 8. Speed and Ping test",
        "opt9": " 9. FULL UNINSTALL (Clean system registries)",
        "opt0": " 0. Exit menu",
        "choice": "Select action (0-9): ",
        "link_title": "\n Telegram Link:",
        "press_enter": "\nPress Enter to return to menu...",
        "enter_port": "\nEnter new port (current {}): ",
        "port_changed": " Port changed. Restart proxy (option 6).",
        "enter_login": "\nEnter new username (current {}): ",
        "login_changed": " Username changed.",
        "enter_pass": "\nEnter new password (current {}): ",
        "pass_changed": " Password changed.",
        "new_pass_gen": " New password generated: {}",
        "restarting": "\n Starting background process in Windows...",
        "restarted": " Proxy successfully started in background!",
        "stopping": "\n Stopping background process...",
        "stopped": " Background proxy stopped.",
        "testing": "\nTesting speed and ping...",
        "test_res": " Test Results:\n   - Ping: {:.1f} ms\n   - Download Speed: {:.2f} Mbps",
        "test_fail": " Test failed: Servers are unreachable.",
        "uninstalling": "\nRemoving matg command and configs from Windows...",
        "uninstalled": "Script cleared from system.",
        "init_done": "\n Setup complete! Command 'matg' is registered.",
    }
}

def load_config():
    global PORT, USER, PASSWORD, LANG
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
                if len(lines) >= 4:
                    PORT = int(lines[0])
                    USER = lines[1]
                    PASSWORD = lines[2]
                    LANG = lines[3]
        except Exception:
            pass

def save_config():
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            f.write(f"{PORT}\n{USER}\n{PASSWORD}\n{LANG}\n")
    except Exception:
        pass

load_config()

async def handle_client(reader, writer):
    try:
        header = await reader.readexactly(2)
        if header[0] != 0x05:
            writer.close()
            return
        nmethods = header[1]
        methods = await reader.readexactly(nmethods)
        if 0x02 not in methods:
            writer.write(b"\x05\xff")
            await writer.drain()
            writer.close()
            return
        writer.write(b"\x05\x02")
        await writer.drain()
        auth_header = await reader.readexactly(2)
        if auth_header[0] != 0x01:
            writer.close()
            return
        user_len = auth_header[1]
        username = (await reader.readexactly(user_len)).decode()
        pass_len = (await reader.readexactly(1))[0]
        password = (await reader.readexactly(pass_len)).decode()

        if username != USER or password != PASSWORD:
            writer.write(b"\x01\x01")
            await writer.drain()
            writer.close()
            return
        writer.write(b"\x01\x00")
        await writer.drain()
        req_header = await reader.readexactly(4)
        cmd = req_header[1]
        atyp = req_header[3]
        if cmd != 0x01:
            writer.write(b"\x05\x07")
            await writer.drain()
            writer.close()
            return
        if atyp == 0x01:
            dest_addr = ".".join(str(b) for b in await reader.readexactly(4))
        elif atyp == 0x03:
            domain_len = (await reader.readexactly(1))[0]
            dest_addr = (await reader.readexactly(domain_len)).decode()
        else:
            writer.close()
            return
        dest_port = int.from_bytes(await reader.readexactly(2), "big")
        try:
            remote_reader, remote_writer = await asyncio.open_connection(dest_addr, dest_port)
        except Exception:
            writer.write(b"\x05\x01")
            await writer.drain()
            writer.close()
            return
        writer.write(b"\x05\x00\x00\x01\x00\x00\x00\x00\x00\x00")
        await writer.drain()

        async def tunnel(src, dst):
            try:
                while True:
                    data = await src.read(4096)
                    if not data:
                        break
                    dst.write(data)
                    await dst.drain()
            except Exception:
                pass
            finally:
                dst.close()

        asyncio.create_task(tunnel(reader, remote_writer))
        asyncio.create_task(tunnel(remote_reader, writer))
    except Exception:
        writer.close()

def is_proxy_running():
    """Проверка, запущен ли уже скрытый процесс питона с нашим портом."""
    cmd = f'wmic process where "CommandLine like \'%--daemon%\'" get CommandLine'
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return "--daemon" in res.stdout

def start_proxy_background():
    """Запуск прокси в полностью скрытом режиме Windows через VBScript."""
    stop_proxy_background()
    script_path = os.path.abspath(__file__)
    
    # Создаем скрытый батник-пускач
    with open(BAT_RUNNER, "w", encoding="utf-8") as f:
        f.write(f'@echo off\npython "{script_path}" --daemon\n')
        
    # Создаем VBS скрипт, который запускает батник БЕЗ появления черного окна консоли
    with open(VBS_RUNNER, "w", encoding="utf-8") as f:
        f.write(f'Set WshShell = CreateObject("WScript.Shell")\nWshShell.Run chr(34) & "{BAT_RUNNER}" & chr(34), 0, False\n')
        
    # Запуск VBS-скрипта в системе
    os.startfile(VBS_RUNNER)

def stop_proxy_background():
    """Остановка фонового процесса питона в Windows."""
    cmd = 'wmic process where "CommandLine like \'%--daemon%\'" call terminate'
    subprocess.run(cmd, shell=True, capture_output=True)

def setup_windows_cli():
    """Создание команды 'matg' в Windows через добавление bat-файла в директорию путей."""
    script_path = os.path.abspath(__file__)
    # Путь к системной папке Windows для пользовательских CLI утилит
    win_cmd_dir = os.path.join(os.environ["USERPROFILE"], "AppData\\Local\\Microsoft\\WindowsApps")
    cli_bat = os.path.join(win_cmd_dir, "matg.cmd")
    
    with open(cli_bat, "w", encoding="utf-8") as f:
        f.write(f'@echo off\npython "{script_path}"\n')

def full_uninstall_win():
    txt = STRINGS[LANG]
    print(txt["uninstalling"])
    stop_proxy_background()
    
    win_cmd_dir = os.path.join(os.environ["USERPROFILE"], "AppData\\Local\\Microsoft\\WindowsApps")
    cli_bat = os.path.join(win_cmd_dir, "matg.cmd")
    
    for file in [CONFIG_FILE, VBS_RUNNER, BAT_RUNNER, cli_bat]:
        if os.path.exists(file):
            try: os.remove(file)
            except Exception: pass
            
    print(txt["uninstalled"])
    try: os.remove(os.path.abspath(__file__))
    except Exception: pass
    sys.exit(0)

def test_telegram_speed():
    txt = STRINGS[LANG]
    print(txt["testing"])
    test_url = "https://1.1.1.1/cdn-cgi/trace"
    pings = []

    for _ in range(3):
        try:
            t0 = time.time()
            req = urllib.request.Request(test_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=3) as r:
                r.read(100)
            pings.append((time.time() - t0) * 1000)
        except Exception: pass

    if not pings:
        print(txt["test_fail"])
        return

    avg_ping = sum(pings) / len(pings)
    speed_mbps = 0.0

    try:
        t0 = time.time()
        speed_url = "https://speed.cloudflare.com/__down?bytes=1000000"
        req = urllib.request.Request(speed_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            data = r.read()
        duration = time.time() - t0
        if duration > 0:
            data_size_bits = len(data) * 8
            speed_mbps = (data_size_bits / duration) / (1024 * 1024)
    except Exception: pass

    print("\n" + "=" * 40)
    print(txt["test_res"].format(avg_ping, speed_mbps))
    print("=" * 40)

def get_tg_link():
    try:
        ip = urllib.request.urlopen("https://ifconfig.me/ip", timeout=3).read().decode().strip()
    except Exception:
        ip = "127.0.0.1"
    return f"https://t.me/socks?server={ip}&port={PORT}&user={USER}&pass={PASSWORD}"

def show_menu():
    global PORT, USER, PASSWORD
    while True:
        txt = STRINGS[LANG]
        os.system("cls")
            
        print("=" * 50)
        print(txt["title"])
        print("=" * 50)
        print(txt["status"], end="")
        
        if is_proxy_running():
            print("\033[92m" + txt["active"].format(PORT) + "\033[0m")
        else:
            print("\033[91m" + txt["inactive"] + "\033[0m")

        print(txt["login"].format(USER))
        print(txt["pass"].format(PASSWORD))
        print("-" * 50)
        print(txt["opt1"])
        print(txt["opt2"])
        print(txt["opt3"])
        print(txt["opt4"])
        print(txt["opt5"])
        print(txt["opt6"])
        print(txt["opt7"])
        print(txt["opt8"])
        print("\033[91m" + txt["opt9"] + "\033[0m")
        print(txt["opt0"])
        print("=" * 50)

        choice = input(txt["choice"]).strip()

        if choice == "1":
            print(txt["link_title"])
            print(f"{get_tg_link()}")
            input(txt["press_enter"])
        elif choice == "2":
            new_port = input(txt["enter_port"].format(PORT)).strip()
            if new_port.isdigit():
                PORT = int(new_port)
                save_config()
                print(txt["port_changed"])
            input(txt["press_enter"])
        elif choice == "3":
            new_user = input(txt["enter_login"].format(USER)).strip()
            if new_user:
                USER = new_user
                save_config()
                print(txt["login_changed"])
            input(txt["press_enter"])
        elif choice == "4":
            new_pass = input(txt["enter_pass"].format(PASSWORD)).strip()
            if new_pass:
                PASSWORD = new_pass
                save_config()
                print(txt["pass_changed"])
            input(txt["press_enter"])
        elif choice == "5":
            PASSWORD = secrets.token_hex(8)
            save_config()
            print(txt["new_pass_gen"].format(PASSWORD))
            input(txt["press_enter"])
        elif choice == "6":
            print(txt["restarting"])
            save_config()
            start_proxy_background()
            print(txt["restarted"])
            print(f"{txt['link_title']}\n{get_tg_link()}")
            input(txt["press_enter"])
        elif choice == "7":
            print(txt["stopping"])
            stop_proxy_background()
            print(txt["stopped"])
            input(txt["press_enter"])
        elif choice == "8":
            test_telegram_speed()
            input(txt["press_enter"])
        elif choice == "9":
            confirm = input("\n Are you sure? (y/n): ").strip()
            if confirm.lower() in ["y", "yes", "д", "да"]:
                full_uninstall_win()
        elif choice == "0":
            break

async def run_server():
    server = await asyncio.start_server(handle_client, "0.0.0.0", PORT)
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    if "--daemon" in sys.argv:
        asyncio.run(run_server())
    else:
        # Первый запуск — инициализация
        if not os.path.exists(CONFIG_FILE):
            os.system("cls")
            print("Choose language. (Выберите язык прокси-панели)")
            print("1. English")
            print("2. Русский")
            l_choice = input("Select (1-2): ").strip()
            LANG = "en" if l_choice == "1" else "ru"
            save_config()
            setup_windows_cli()
            start_proxy_background()
            print(STRINGS[LANG]["init_done"])
            print(f"{STRINGS[LANG]['link_title']}\n{get_tg_link()}")
            print("\nТеперь вы можете вызывать это меню из любой папки Windows по команде: matg")
            sys.exit(0)

        show_menu()
