import asyncio
import logging
from typing import Tuple

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    WebAppInfo,
)

from app.core.config import settings

router = Router()


def build_webapp_url() -> str | None:
    url = settings.webapp_url
    if not url:
        return None
    return str(url).rstrip("/")


def build_keyboards(webapp_url: str | None) -> Tuple[ReplyKeyboardMarkup | None, InlineKeyboardMarkup | None]:
    if not webapp_url:
        return None, None

    reply_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="Открыть Quadrant",
                    web_app=WebAppInfo(url=webapp_url),
                )
            ]
        ],
        resize_keyboard=True,
        is_persistent=True,
    )

    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открыть Mini App",
                    web_app=WebAppInfo(url=webapp_url),
                )
            ],
            [
                InlineKeyboardButton(
                    text="Открыть в браузере",
                    url=webapp_url,
                )
            ],
        ]
    )

    return reply_keyboard, inline_keyboard


@router.message(CommandStart())
async def handle_start(message: types.Message) -> None:
    webapp_url = build_webapp_url()
    reply_keyboard, inline_keyboard = build_keyboards(webapp_url)

    lines = [
        "🚀 Quadrant Mini App — тот же интерфейс и данные, что и в iOS.",
        "Нажми кнопку ниже, чтобы открыть Mini App прямо в Telegram и авторизоваться.",
    ]
    if not webapp_url:
        lines.append("⚠️ Установи WEBAPP_URL, чтобы кнопка открытия заработала.")

    await message.answer("\n".join(lines), reply_markup=reply_keyboard)
    if inline_keyboard:
        await message.answer("Открыть приложение:", reply_markup=inline_keyboard)


@router.message(Command("help"))
async def handle_help(message: types.Message) -> None:
    webapp_url = build_webapp_url()
    lines = [
        "1) Убедись, что Mini App доступен по HTTPS (Vercel или ngrok).",
        "2) Нажми «Открыть Quadrant» — Mini App откроется с тем же аккаунтом.",
        "3) Внутри Mini App данные подтягиваются через X-Telegram-Init-Data.",
    ]
    if webapp_url:
        lines.append(f"Ссылка на Mini App: {webapp_url}")
    await message.answer("\n".join(lines))


@router.message()
async def handle_fallback(message: types.Message) -> None:
    webapp_url = build_webapp_url()
    reply_keyboard, inline_keyboard = build_keyboards(webapp_url)
    text = "Напиши /start, чтобы открыть Mini App."
    if not webapp_url:
        text += "\nАдрес Mini App не настроен (WEBAPP_URL)."
    await message.answer(text, reply_markup=reply_keyboard)
    if inline_keyboard:
        await message.answer("Открыть приложение:", reply_markup=inline_keyboard)


async def on_startup(bot: Bot) -> None:
    await bot.set_my_commands(
        [
            types.BotCommand(command="start", description="Запустить Mini App"),
            types.BotCommand(command="help", description="Как пользоваться ботом"),
        ]
    )


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    if not settings.telegram_bot_token or settings.telegram_bot_token == "dummy":
        raise RuntimeError("TELEGRAM_BOT_TOKEN не задан")

    bot = Bot(token=settings.telegram_bot_token, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(router)

    webapp_url = build_webapp_url()
    if not webapp_url:
        logging.warning("WEBAPP_URL не задан — кнопки открытия Mini App не будут работать.")

    await bot.delete_webhook(drop_pending_updates=True)
    await on_startup(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
