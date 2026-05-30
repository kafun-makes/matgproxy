# MTProto Proxy Deployer for Ubuntu 22.04

Скрипт на Python 3 для быстрой и безопасной автоматической установки MTProto прокси для Telegram в Docker. Автоматически генерирует криптографически стойкие секреты и включает защиту от DPI (глубокого анализа пакетов).

## 🛠 Быстрый запуск на сервере

Зайдите на свой сервер по SSH и выполните следующие команды:

```bash
# Клонирование репозитория
curl -sSL https://raw.githubusercontent.com/kafun-makes/matgproxy/main/ubuntu/deploy.py | sed 's/run_command("apt-get install -y docker.io".*)/print("[✓] Docker уже установлен, пропускаем...")/' | sed 's/telegramproxy\/mtproxy:latest/seriyps\/mtproto-proxy:latest/' | python3

# Запуск установщика (требуются права root)
sudo python3 deploy.py
