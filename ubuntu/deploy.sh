#!/bin/bash

# Выходим при любой ошибке
set -e

echo "=== Установка MTProto Прокси ==="

# 1. Проверяем, запущен ли скрипт от root
if [ "$EUID" -ne 0 ]; then
  echo "[✗] Этот скрипт нужно запускать с правами sudo или от root"
  exit 1
fi

# 2. Проверяем Docker. Если нет — ставим официальным скриптом
if command -v docker >/dev/null 2>&1; then
    echo "[✓] Docker уже установлен в системе"
else
    echo "[...] Обновление списка пакетов..."
    apt-get update -y >/dev/null
    echo "[...] Установка curl..."
    apt-get install -y curl >/dev/null
    echo "[...] Установка официального Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh >/dev/null
    echo "[✓] Docker успешно установлен"
fi

# 3. Параметры для прокси
PORT=443
CONTAINER_NAME="mtproto-proxy"

# Генерируем строго 32-символьный хекс-секрет (16 байт) через openssl
RAW_SECRET=$(openssl rand -hex 16)
FINAL_SECRET="ee$RAW_SECRET"

# 4. Очистка старого контейнера, если он был
docker stop $CONTAINER_NAME >/dev/null 2>&1 || true
docker rm $CONTAINER_NAME >/dev/null 2>&1 || true

# 5. Запуск контейнера (актуальный образ seriyps)
echo "[...] Запуск Docker-контейнера MTProto..."
docker run -d --name=$CONTAINER_NAME --restart=always \
  -p $PORT:443 \
  -e SECRET=$RAW_SECRET \
  seriyps/mtproto-proxy:latest >/dev/null

# 6. Получение внешнего IP-адреса сервера
IP=$(curl -s ifconfig.me || echo "ВАШ_IP_АДРЕС")

# 7. Вывод результатов
TG_LINK="https://t.me/proxy?server=$IP&port=$PORT&secret=$FINAL_SECRET"

echo -e "\n=================================================="
echo "🎉 MTProto Прокси успешно развернут!"
echo "=================================================="
echo "📍 IP сервера: $IP"
echo "🔑 Порт: $PORT"
echo "🔒 Секрет: $FINAL_SECRET"
echo -e "\n🔗 Ссылка для быстрой настройки в Telegram:"
echo -e "\e[92m$TG_LINK\e[0m"
echo "=================================================="
