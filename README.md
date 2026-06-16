# PolyWallpaperBot

Интеллектуальный чат-бот для продажи обоев — курсовая работа по варианту **«Бот для продажи обоев»**.

## Характеристики бота (претендуемая оценка: **85% — «хорошо»**)

| Характеристика | Реализовано |
|---|---|
| Минимальные функции вопрос-ответ | ✅ |
| Расширенный датасет намерений | ✅ |
| Датасет диалогов `dialogues.txt` | ✅ |
| ML для анализа намерений (sklearn) | ✅ |
| API Telegram | ✅ |
| Сценарии рекламы товара | ✅ |
| Не менее 3 товаров | ✅ (3 коллекции обоев) |
| Голосовые команды | ❌ |

## Возможности

- **NLP**: очистка ввода, расстояние Левенштейна, анализ тональности
- **ML**: `TfidfVectorizer` + `LinearSVC` для классификации намерений
- **Темы диалога**: контекстные сценарии (комната → коллекция → заказ)
- **Датасет диалогов**: поиск типовых ответов из `dialogues.txt`
- **Каталог**: 3 коллекции обоев с ценами и характеристиками
- **Реклама**: ненавязчивые вставки после нескольких сообщений
- **Telegram**: команды `/start`, `/help`, `/catalog`

## Быстрый старт

### 1. Установка зависимостей

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Датасет диалогов

Для полной версии скачайте `dialogues.txt` (~133 МБ) и положите в `data/dialogues.txt`.

Для тестирования уже есть `data/dialogues_sample.txt` — бот использует его автоматически, если полный файл отсутствует.

### 3. Telegram-бот

1. Создайте бота через [@BotFather](https://t.me/BotFather)
2. Скопируйте `.env.example` → `.env` и вставьте токен:

```bash
cp .env.example .env
```

3. Запуск:

```bash
python run_telegram.py
```

### 4. Консольный режим (без Telegram)

```bash
python run_console.py
```

## Структура проекта

```
PolyWallpaperBot/
├── data/
│   ├── dialogues_sample.txt   # образец датасета
│   └── dialogues.txt          # полный датасет (скачать отдельно)
├── src/
│   ├── config.py              # намерения и каталог товаров
│   ├── nlp.py                 # очистка, тональность
│   ├── intents.py             # ML-классификатор, темы
│   ├── dialogues.py           # поиск по датасету
│   ├── products.py            # реклама и каталог
│   └── bot_core.py            # ядро бота
├── run_console.py
├── run_telegram.py
└── requirements.txt
```

## Примеры диалога

```
> Привет
< Здравствуйте! Я консультант магазина обоев «Политех»...

> Покажи обои
< 🎨 Наш каталог обоев: Лесная сказка, Парижские мотивы, Геометрия Pro...

> Обои для спальни
< Для спальни отлично подойдут спокойные тона «Лесной сказки»...

> Лесная сказка
< 📋 Лесная сказка — флизелин, 2500 ₽/рулон...

> Хочу купить
< Отличный выбор! Какую коллекцию хотите заказать?
```

## Каталог товаров

| Коллекция | Материал | Цена |
|---|---|---|
| Лесная сказка | флизелин | 2500 ₽ |
| Парижские мотивы | винил на флизелине | 1800 ₽ |
| Геометрия Pro | винил | 1200 ₽ |

## Деплой на VPS (GitHub Actions)

При каждом `push` в `main` GitHub Actions подключается по SSH к серверу и выполняет `git pull` + перезапуск бота.

### Шаг 1. Запушить код

```bash
git add .
git commit -m "Add wallpaper bot and deploy pipeline"
git push origin main
```

### Шаг 2. Первичная настройка VPS (один раз, в веб-консоли)

```bash
apt install -y git curl
curl -fsSL https://raw.githubusercontent.com/Ay0wa/PolyWallpaperBot/main/deploy/setup-server.sh -o setup-server.sh
bash setup-server.sh
nano /opt/PolyWallpaperBot/.env   # вставить TELEGRAM_BOT_TOKEN
systemctl restart wallpaper-bot
systemctl status wallpaper-bot
```

### Шаг 3. SSH-ключ для GitHub Actions

**На своём ПК:**

```bash
ssh-keygen -t ed25519 -C "github-actions-deploy" -f github_deploy -N ""
```

**На VPS (веб-консоль):**

```bash
mkdir -p /root/.ssh && chmod 700 /root/.ssh
nano /root/.ssh/authorized_keys   # вставить содержимое github_deploy.pub
chmod 600 /root/.ssh/authorized_keys
```

Убедитесь, что в панели VPS **открыт порт 22** (SSH) — иначе GitHub не сможет подключиться.

### Шаг 4. Секреты в GitHub

Репозиторий → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**:

| Secret | Значение |
|---|---|
| `VPS_HOST` | IP сервера, например `37.1.215.45` |
| `VPS_USER` | `root` |
| `VPS_SSH_KEY` | содержимое файла `github_deploy` (приватный ключ) |

### Шаг 5. Проверка

Сделайте любой коммит и `git push` — во вкладке **Actions** должен пройти workflow **Deploy to VPS**.

Логи бота на сервере:

```bash
journalctl -u wallpaper-bot -f
```

### Ручной деплой на сервере

```bash
bash /opt/PolyWallpaperBot/deploy/deploy.sh
```
