# Quadrant Backend

FastAPI + PostgreSQL сервисная архитектура для мобильного приложения Quadrant.

## Стек
- FastAPI / Uvicorn
- PostgreSQL (asyncpg + SQLAlchemy 2.x)
- Alembic миграции
- Celery + Redis для фоновых задач (Strava/Notion sync, уведомления)
- Pydantic Settings для конфигурации

## Запуск (локально)
```bash
poetry install
poetry run uvicorn app.main:app --reload
```

Перед запуском заполните `.env` (см. `app/core/config.py`) или переменные окружения:
- `DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/quadrant`
- `REDIS_URL=redis://localhost:6379/0`
- `JWT_SECRET=...`
- `TELEGRAM_BOT_TOKEN=...`
- `WEBAPP_URL=https://<ваш-домен-с-mini-app>` (Vercel или ngrok HTTPS урл)

## Структура
```
app/
  api/          # Роутеры и зависимости
  core/         # Конфиг, логирование, безопасность, база
  models/       # SQLAlchemy модели
  repositories/ # CRUD-слой
  schemas/      # Pydantic DTO
  services/     # Бизнес-логика
  integrations/ # Strava, TonConnect, Notion
  tasks/        # Celery задачи
  bot/          # Aiogram бот с кнопкой запуска Telegram Mini App
```

## Telegram бот (Mini App)
Бот запускает тот же интерфейс, что и iOS-приложение, через Telegram Mini App.

1. Убедись, что фронт доступен по HTTPS (Vercel или `ngrok http 19006`) и в .env фронта заданы `EXPO_PUBLIC_API_URL` и `EXPO_PUBLIC_TELEGRAM_BOT_ID`.
2. В `.env` backend задай `TELEGRAM_BOT_TOKEN` и `WEBAPP_URL` (домен фронта, например `https://your-app.vercel.app`).
3. Запусти бота: `poetry run python -m app.bot.main`
4. В Telegram набери `/start` — появится кнопка «Открыть Quadrant», Mini App откроется внутри Telegram. Авторизация и данные синхронизируются через `X-Telegram-Init-Data`.

### Локальная проверка через ngrok
- Backend: `poetry run uvicorn app.main:app --reload --port 8001` и `ngrok http 8001` → URL подставь в `EXPO_PUBLIC_API_URL` фронта.
- Front (Expo web): `npx expo start --web --port 19006` и `ngrok http 19006` → URL подставь в `WEBAPP_URL` и `EXPO_PUBLIC_WEBAPP_URL` (если используешь).
- Бот: `poetry run python -m app.bot.main` (long polling, без вебхука). В BotFather укажи Mini App кнопку с тем же `WEBAPP_URL`.

## Следующие шаги
1. Настроить Alembic и описать первичные модели (User, Course, Book и т.д.).
2. Реализовать Telegram OAuth-флоу и JWT-авторизацию.
3. Поднять docker-compose c Postgres и Redis.
4. Подключить Strava/Ton/Notion интеграции.
