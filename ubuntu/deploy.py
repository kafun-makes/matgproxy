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
        print("[✗] Этот скрипт нужно запускать с правами sudo")
        sys.exit(1)

    print("=== Установка MTProto Прокси ===")

    # 1. Проверяем, установлен ли Docker. Если нет — ставим официальным скриптом
    if subprocess.run("type docker", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
        print("[✓] Docker уже установлен в системе")
    else:
        run_command("apt-get update", "Обновление списка пакетов")
        run_command("apt-get install -y curl", "Установка curl")
        run_command("curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh", "Установка официального Docker")

    # 2. Параметры для прокси
    port = 443 
    secret = secrets.token_hex(16)
    container_name = "mtproto-proxy"

    # 3. Очистка старого контейнера
    subprocess.run(f"docker stop {container_name}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(f"docker rm {container_name}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 4. Запуск контейнера (используем стабильный форк seriyps)
    docker_cmd = (
        f"docker run -d --name={container_name} --restart=always "
        f"-p {port}:443 -e SECRET={secret} seriyps/mtproto-proxy:latest"
    )
    run_command(docker_cmd, "Запуск Docker-контейнера MTProto")

    # 5. Получение внешнего IP-адреса
    try:
        ip = subprocess.check_output("curl -s ifconfig.me", shell=True).decode('utf-8').strip()
    except Exception:
        ip = "ВАШ_IP_АДРЕС"

    # 6. Формирование ссылки с DPI защитой (префикс ee)
    tg_link = f"https://t.me/proxy?server={ip}&port={port}&secret=ee{secret}"

    print("\n" + "="*50)
    print("🎉 MTProto Прокси успешно развернут!")
    print("="*50)
    print(f"📍 IP сервера: {ip}")
    print(f"🔑 Порт: {port}")
    print(f"🔒 Секрет: ee{secret}")
    print("\n🔗 Ссылка для быстрой настройки в Telegram:")
    print(f"\033[92m{tg_link}\033[0m")
    print("="*50)

if __name__ == "__main__":
    main()
