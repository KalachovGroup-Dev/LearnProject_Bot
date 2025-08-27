import asyncio
import logging
from aiogram import Bot, Dispatcher
from handlers.handlers_routes import router as common_router

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Замените "YOUR_BOT_TOKEN" на токен, который вы получили от BotFather
from token_bot import load_token
API_TOKEN = load_token()

# Объект бота
bot = Bot(token=API_TOKEN)
# Диспетчер
dp = Dispatcher()

# Запуск процесса поллинга новых апдейтов
async def main():
    # Подключаем роутер
    dp.include_router(common_router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())