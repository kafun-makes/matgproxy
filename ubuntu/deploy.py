#!/usr/bin/env python3
import os
import secrets
import subprocess
import sys

def run_command(command, description):
    """Вспомогательная функция для запуска системных команд"""
    print(f"[...] {description}")
    try:
        subprocess.run(command, shell=True, check=True, stdout=subprocess.DEVNULL)
        print(f"[✓] Успешно: {description}")
    except subprocess.CalledProcessError:
        print(f"[✗] Ошибка при выполнении: {description}")
        sys.exit(1)

def main():
    # Проверка на права суперпользователя
    if os.getuid() != 0:
        print("[✗] Этот скрипт нужно запускать с правами sudo (sudo python3 deploy.py)")
        sys.exit(1)

    print("=== Установка MTProto Прокси ===")

    # 1. Обновление пакетов и установка Docker
    run_command("apt-get update", "Обновление списка пакетов")
    run_command("apt-get install -y docker.io", "Установка Docker")

    # 2. Генерация параметров для прокси
    # Порт можно изменить на любой удобный
    port = 443 
    # Генерируем случайный 32-символьный шестнадцатеричный секрет
    secret = secrets.token_hex(16)
    
    # Имя контейнера
    container_name = "mtproto-proxy"

    # 3. Остановка старого контейнера, если он есть
    subprocess.run(f"docker stop {container_name}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(f"docker rm {container_name}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 4. Запуск Docker-контейнера (используем проверенный образ от Telegram)
    docker_cmd = (
        f"docker run -d --name={container_name} --restart=always "
        f"-p {port}:443 -e SECRET={secret} seriyps/mtproto-proxy:latest"
    )
    run_command(docker_cmd, "Запуск Docker-контейнера MTProto")

    # 5. Получение внешнего IP-адреса сервера
    try:
        ip = subprocess.check_output("curl -s ifconfig.me", shell=True).decode('utf-8').strip()
    except Exception:
        ip = "ВАШ_IP_АДРЕС"

    # 6. Формирование ссылки для подключения
    # Используем префикс 'ee' для защиты от блокировок (глубокого анализа пакетов / DPI)
    tg_link = f"https://t.me/proxy?server={ip}&port={port}&secret=ee{secret}"

    print("\n" + "="*50)
    print("🎉 MTProto Прокси успешно развернут и запущен!")
    print("="*50)
    print(f"📍 IP сервера: {ip}")
    print(f"🔑 Порт: {port}")
    print(f"🔒 Секрет (с DPI префиксом): ee{secret}")
    print("\n🔗 Ссылка для быстрой настройки в Telegram:")
    print(f"\033[92m{tg_link}\033[0m")
    print("="*50)

if __name__ == "__main__":
    main()
