# MTProto Proxy Deployer for Ubuntu 22.04

Скрипт на Python 3 для быстрой и безопасной автоматической установки MTProto прокси для Telegram в Docker. Автоматически генерирует криптографически стойкие секреты и включает защиту от DPI (глубокого анализа пакетов).

## 🛠 Быстрый запуск на сервере

Зайдите на свой сервер по SSH и выполните следующие команды:

```bash
# Клонирование репозитория
git clone [https://github.com/kafun-makes/matgproxy.git](https://github.com/kafun-makes/matgproxy.git)
cd matgproxy

# Запуск установщика (требуются права root)
sudo python3 deploy.py
