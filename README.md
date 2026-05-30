# Telegram MTProto Proxy Installer

Простой Bash-скрипт для автоматического и мгновенного развертывания персонального MTProto-прокси для Telegram на серверах Ubuntu одной командой.

В качестве ядра используется современный и быстрый прокси-сервер **mtg** (написан на Go/C), который автоматически маскирует трафик под обычный Fake TLS (`ee`-секреты) для надежного обхода DPI блокировок.

## Требования
* VPS с операционной системой Ubuntu (тестировалось на Ubuntu 22.04).
* Доступ к пользователю с правами `sudo`.

## Быстрая установка одной командой

Просто подключитесь к вашему VPS по SSH и вставьте следующую команду:

```bash
sudo bash -c "$(curl -sSfL [https://raw.githubusercontent.com/kafun-makes/matgproxy/main/ubuntu/matg](https://raw.githubusercontent.com/kafun-makes/matgproxy/main/ubuntu/matg))"
