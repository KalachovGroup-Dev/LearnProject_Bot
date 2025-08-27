import asyncio
import logging
from aiogram import Bot, Dispatcher

from handlers.handlers_routes import router as common_router # Маршрутизация
from database.db import * # Управление БД
from config import API_TOKEN, DB_NAME # Загрузка конфига

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Объект бота
bot = Bot(token=API_TOKEN)
# Диспетчер
dp = Dispatcher()

# Запуск процесса поллинга новых апдейтов
async def main():
    # Подключаем роутер
    dp.include_router(common_router)

    # Запускаем создание таблицы базы данных
    await create_table()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())