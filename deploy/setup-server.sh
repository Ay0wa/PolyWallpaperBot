#!/bin/bash
# Однократная настройка VPS (запускать в веб-консоли от root)
set -euo pipefail

APP_DIR="/opt/PolyWallpaperBot"
REPO_URL="${REPO_URL:-https://github.com/Ay0wa/PolyWallpaperBot.git}"
SERVICE_NAME="wallpaper-bot"

echo "==> Установка пакетов..."
apt-get update -qq
apt-get install -y git python3-venv python3-pip curl

echo "==> Клонирование репозитория..."
if [ -d "$APP_DIR/.git" ]; then
    cd "$APP_DIR"
    git pull origin main
else
    git clone "$REPO_URL" "$APP_DIR"
    cd "$APP_DIR"
fi

echo "==> Виртуальное окружение..."
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q

if [ ! -f .env ]; then
    cp .env.example .env
    echo ""
    echo "!!! Создан $APP_DIR/.env — вставьте TELEGRAM_BOT_TOKEN:"
    echo "    nano $APP_DIR/.env"
    echo ""
fi

echo "==> Установка systemd-сервиса..."
cp deploy/wallpaper-bot.service /etc/systemd/system/${SERVICE_NAME}.service
systemctl daemon-reload
systemctl enable ${SERVICE_NAME}

if grep -q "your_bot_token" .env 2>/dev/null; then
    echo "Заполните .env перед запуском: nano $APP_DIR/.env"
else
    systemctl restart ${SERVICE_NAME}
    echo "Бот запущен. Статус: systemctl status ${SERVICE_NAME}"
fi

echo ""
echo "Готово. Директория: $APP_DIR"
echo "Логи: journalctl -u ${SERVICE_NAME} -f"
