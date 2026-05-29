#!/usr/bin/env python3
import asyncio
import os
import secrets
import subprocess
import sys
import time
import urllib.request

CONFIG_FILE = "/etc/tg_proxy_config.txt"
PORT = 2438  # Жестко прописан ваш порт
USER = "tg_user"
# Для MTProto v2 (движка mtg) нужен секрет со специальным префиксом ee для Fake-TLS
SECRET = "ee" + secrets.token_hex(16)
LANG = "ru"

STRINGS = {
    "ru": {
        "title": "         УПРАВЛЕНИЕ MTPROTO ПРОКСИ [matg]        ",
        "status": " Текущий статус службы: ",
        "active": "РАБОТАЕТ (ПОРТ: {})",
        "inactive": "ОСТАНОВЛЕН",
        "login": " Текущий Логин (для меню): {}",
        "pass": " Текущий Секрет (Secret): {}",
        "opt1": " 1. Показать ссылку для подключения в Telegram",
        "opt2": " 2. Изменить ПОРТ прокси",
        "opt3": " 3. Изменить ЛОГИН",
        "opt4": " 4. Изменить СЕКРЕТ вручную",
        "opt5": " 5. Сгенерировать новый случайный Секрет",
        "opt6": " 6. Запустить / Перезапустить прокси",
        "opt7": " 7. Остановить прокси",
        "opt8": " 8. Тест скорости и пинга до Telegram",
        "opt9": " 9. ПОЛНОЕ УДАЛЕНИЕ (Деинсталляция)",
        "opt0": " 0. Выйти из меню",
        "choice": "Выберите действие (0-9): ",
        "link_title": "\n Ссылка для Telegram:",
        "press_enter": "\nНажмите Enter для возврата в меню...",
        "enter_port": "\nВведите новый порт (сейчас {}): ",
        "port_changed": " Порт изменен. Не забудьте перезапустить прокси (пункт 6).",
        "enter_login": "\nВведите новый логин (сейчас {}): ",
        "login_changed": " Логин изменен.",
        "enter_pass": "\nВведите новый секрет (32 hex-символа, желательно с ee): ",
        "pass_changed": " Секрет изменен.",
        "new_pass_gen": " Сгенерирован новый секрет: {}",
        "restarting": "\n Перезапуск службы...",
        "restarted": " MTProto Прокси успешно перезапущен!",
        "stopping": "\n Остановка службы...",
        "stopped": " Прокси остановлен.",
        "testing": "\nТестирование скорости соединения с Telegram...",
        "test_res": " Результаты теста:\n   - Пинг: {:.1f} мс\n   - Скорость скачивания: {:.2f} Мбит/с",
        "test_fail": " Ошибка теста: Серверы Telegram недоступны с этого VPS.",
        "uninstalling": "\nНачинаем полное удаление прокси из системы...",
        "uninstalled": "Прокси полностью удален. Команда matg больше недоступна.",
        "init_done": "\n Настройка завершена! Команда 'matg' зарегистрирована.",
    },
    "en": {
        "title": "         MTPROTO PROXY MANAGEMENT [matg]        ",
        "status": " Current service status: ",
        "active": "RUNNING (PORT: {})",
        "inactive": "STOPPED",
        "login": " Current Username: {}",
        "pass": " Current Secret: {}",
        "opt1": " 1. Show Telegram connection link",
        "opt2": " 2. Change proxy PORT",
        "opt3": " 3. Change USERNAME",
        "opt4": " 4. Change SECRET manually",
        "opt5": " 5. Generate new random Secret",
        "opt6": " 6. Start / Restart proxy",
        "opt7": " 7. Stop proxy",
        "opt8": " 8. Speed and Ping test to Telegram",
        "opt9": " 9. FULL UNINSTALL (Remove completely)",
        "opt0": " 0. Exit menu",
        "choice": "Select action (0-9): ",
        "link_title": "\n Telegram Link:",
        "press_enter": "\nPress Enter to return to menu...",
        "enter_port": "\nEnter new port (current {}): ",
        "port_changed": " Port changed. Don't forget to restart proxy (option 6).",
        "enter_login": "\nEnter new username (current {}): ",
        "login_changed": " Username changed.",
        "enter_pass": "\nEnter new secret (32 hex chars): ",
        "pass_changed": " Secret changed.",
        "new_pass_gen": " New secret generated: {}",
        "restarting": "\n Restarting service...",
        "restarted": " MTProto Proxy successfully restarted!",
        "stopping": "\n Stopping service...",
        "stopped": " Proxy stopped.",
        "testing": "\nTesting speed and ping to Telegram...",
        "test_res": " Test Results:\n   - Ping: {:.1f} ms\n   - Download Speed: {:.2f} Mbps",
        "test_fail": " Test failed: Telegram cores are unreachable from this VPS.",
        "uninstalling": "\nStarting full uninstallation from the system...",
        "uninstalled": "Proxy completely removed. The 'matg' command is now disabled.",
        "init_done": "\n Setup complete! Command 'matg' is registered.",
    },
}

def load_config():
    global PORT, USER, SECRET, LANG
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
                if len(lines) >= 4:
                    PORT = int(lines[0])
                    USER = lines[1]
                    SECRET = lines[2]
                    LANG = lines[3]
        except Exception:
            pass

def save_config():
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            f.write(f"{PORT}\n{USER}\n{SECRET}\n{LANG}\n")
    except Exception as e:
        print(f"Error saving config: {e}")

load_config()

def install_mtg_binary():
    """Скачивает и устанавливает стабильное Go-ядро mtg, если его нет"""
    binary_path = "/usr/local/bin/mtg"
    if os.path.exists(binary_path):
        return True
    
    print("Установка ядра MTProto (mtg)... / Installing MTProto core...")
    arch = subprocess.run("uname -m", shell=True, capture_output=True, text=True).stdout.strip()
    
    if "arm" in arch or "aarch64" in arch:
        url = "https://github.com/9seconds/mtg/releases/download/v2.1.7/mtg-2.1.7-linux-arm64.tar.gz"
        folder = "mtg-2.1.7-linux-arm64"
    else:
        url = "https://github.com/9seconds/mtg/releases/download/v2.1.7/mtg-2.1.7-linux-amd64.tar.gz"
        folder = "mtg-2.1.7-linux-amd64"

    try:
        subprocess.run(f"wget -qO /tmp/mtg.tar.gz {url} || curl -sL -o /tmp/mtg.tar.gz {url}", shell=True, check=True)
        subprocess.run("tar -xzf /tmp/mtg.tar.gz -C /tmp/", shell=True, check=True)
        subprocess.run(f"sudo mv /tmp/{folder}/mtg {binary_path}", shell=True, check=True)
        subprocess.run(f"sudo chmod +x {binary_path}", shell=True, check=True)
        subprocess.run("rm -rf /tmp/mtg*", shell=True)
        return True
    except Exception as e:
        print(f"Ошибка установки ядра: {e}")
        sys.exit(1)

def setup_systemd_and_cli():
    install_mtg_binary()
    script_path = os.path.abspath(__file__)
    
    # ИСПРАВЛЕНО: Теперь аргументы mtg передаются строго по синтаксису движка v2
    # Секрет передается через флаг -s, чтобы systemd не путал его с путем к конфигу
    service_content = f"""[Unit]
Description=Telegram MTProto Proxy Server (mtg)
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/mtg run -b 0.0.0.0:{PORT} -s {SECRET}
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
"""
    try:
        with open("/etc/systemd/system/tg-proxy.service", "w") as f:
            f.write(service_content)
        subprocess.run("sudo systemctl daemon-reload", shell=True, check=True)
        subprocess.run("sudo systemctl enable tg-proxy.service", shell=True, check=True)
        
        cli_path = "/usr/local/bin/matg"
        with open(cli_path, "w") as f:
            f.write(f"#!/bin/bash\nsudo python3 {script_path}\n")
        subprocess.run(f"sudo chmod +x {cli_path}", shell=True, check=True)
    except Exception as e:
        print(f"System setup error: {e}")

def full_uninstall():
    txt = STRINGS[LANG]
    print(txt["uninstalling"])
    subprocess.run("sudo systemctl stop tg-proxy.service 2>/dev/null", shell=True)
    subprocess.run("sudo systemctl disable tg-proxy.service 2>/dev/null", shell=True)
    subprocess.run("sudo rm /etc/systemd/system/tg-proxy.service 2>/dev/null", shell=True)
    subprocess.run("sudo systemctl daemon-reload", shell=True)
    subprocess.run("sudo rm /usr/local/bin/matg 2>/dev/null", shell=True)
    subprocess.run("sudo rm /usr/local/bin/mtg 2>/dev/null", shell=True)
    subprocess.run(f"sudo rm {CONFIG_FILE} 2>/dev/null", shell=True)
    print(txt["uninstalled"])
    try:
        os.remove(os.path.abspath(__file__))
    except Exception:
        pass
    sys.exit(0)

def test_telegram_speed():
    txt = STRINGS[LANG]
    print(txt["testing"])
    test_url = "https://core.telegram.org/cleanhtml"
    pings = []

    for _ in range(3):
        try:
            t0 = time.time()
            req = urllib.request.Request(test_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=3) as r:
                r.read(100)
            pings.append((time.time() - t0) * 1000)
        except Exception:
            pass

    if not pings:
        print(txt["test_fail"])
        return

    avg_ping = sum(pings) / len(pings)
    speed_mbps = 0.0

    try:
        t0 = time.time()
        req = urllib.request.Request(test_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            data = r.read()
        duration = time.time() - t0
        if duration > 0:
            data_size_bits = len(data) * 8
            speed_mbps = (data_size_bits / duration) / (1024 * 1024)
    except Exception:
        pass

    print("\n" + "=" * 40)
    print(txt["test_res"].format(avg_ping, speed_mbps))
    print("=" * 40)

def get_tg_link():
    try:
        ip = (
            urllib.request.urlopen("https://ifconfig.me/ip", timeout=3)
            .read()
            .decode()
            .strip()
        )
    except Exception:
        ip = "YOUR_VPS_IP"
    return f"tg://proxy?server={ip}&port={PORT}&secret={SECRET}"

def show_menu():
    global PORT, USER, SECRET
    while True:
        txt = STRINGS[LANG]
        os.system("clear")
        print("=" * 50)
        print(txt["title"])
        print("=" * 50)
        print(txt["status"], end="")
        status = subprocess.run(
            "systemctl is-active tg-proxy",
            shell=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        if status == "active":
            print("\033[92m" + txt["active"].format(PORT) + "\033[0m")
        else:
            print("\033[91m" + txt["inactive"] + "\033[0m")

        print(txt["login"].format(USER))
        print(txt["pass"].format(SECRET))
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
            print(f"\033[94m{get_tg_link()}\033[0m")
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
            new_pass = input(txt["enter_pass"]).strip()
            if len(new_pass) >= 32:
                SECRET = new_pass
                save_config()
                print(txt["pass_changed"])
            input(txt["press_enter"])
        elif choice == "5":
            SECRET = "ee" + secrets.token_hex(16)
            save_config()
            print(txt["new_pass_gen"].format(SECRET))
            input(txt["press_enter"])
        elif choice == "6":
            print(txt["restarting"])
            save_config()
            setup_systemd_and_cli()
            subprocess.run("sudo systemctl restart tg-proxy", shell=True)
            print(txt["restarted"])
            input(txt["press_enter"])
        elif choice == "7":
            print(txt["stopping"])
            subprocess.run("sudo systemctl stop tg-proxy", shell=True)
            print(txt["stopped"])
            input(txt["press_enter"])
        elif choice == "8":
            test_telegram_speed()
            input(txt["press_enter"])
        elif choice == "9":
            confirm = input(
                "\n Вы уверены, что хотите УДАЛИТЬ всё? (y/n) / Are you sure? (y/n): "
            ).strip()
            if confirm.lower() in ["y", "yes", "д", "да"]:
                full_uninstall()
        elif choice == "0":
            break

if __name__ == "__main__":
    if not os.path.exists("/etc/systemd/system/tg-proxy.service"):
        os.system("clear")
        print("Choose language. (Выберите язык прокси-панели)")
        print("1. English")
        print("2. Русский")
        l_choice = input("Select (1-2): ").strip()
        LANG = "en" if l_choice == "1" else "ru"

        print(STRINGS[LANG]["restarting"])
        save_config()
        setup_systemd_and_cli()
        subprocess.run("sudo systemctl start tg-proxy", shell=True)
        print(STRINGS[LANG]["init_done"])
        print(f"{STRINGS[LANG]['link_title']}\n{get_tg_link()}")
        sys.exit(0)

    show_menu()
        
