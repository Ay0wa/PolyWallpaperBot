#!/bin/bash
# Скрипт деплоя: git pull + зависимости + перезапуск
set -euo pipefail

APP_DIR="/opt/PolyWallpaperBot"
SERVICE_NAME="wallpaper-bot"

cd "$APP_DIR"

echo "==> git pull..."
git fetch origin main
git reset --hard origin/main

echo "==> pip install..."
source .venv/bin/activate
pip install -r requirements.txt -q

echo "==> restart ${SERVICE_NAME}..."
systemctl restart ${SERVICE_NAME}
systemctl is-active --quiet ${SERVICE_NAME}

echo "Deploy OK: $(git rev-parse --short HEAD)"
