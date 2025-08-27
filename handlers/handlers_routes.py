from aiogram import Router, types
from aiogram.filters import Command

# Создаем роутер
router = Router()
# Хэндлер на команду /start
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    # Логика обработки команды /start
    await message.answer("Привет! Я бот для проведения квиза. Введите /quiz, чтобы начать.")

# Хэндлер на команду /quiz
@router.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    # Логика начала квиза
    await message.answer("Давайте начнем квиз! Первый вопрос: ...")