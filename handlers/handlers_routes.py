from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import F

from database.db import * # Управление БД
from questions import get_questions # Загрузка вопросов

questions_list = get_questions(1)
questions_list = questions_list['questions']
# Создаем роутер
router = Router()

def generate_options_keyboard(answer_options, right_answer):
  # Создаем сборщика клавиатур типа Inline
    builder = InlineKeyboardBuilder()

    # В цикле создаем 4 Inline кнопки, а точнее Callback-кнопки
    for index, option in enumerate(answer_options):
        builder.add(types.InlineKeyboardButton(
            # Текст на кнопках соответствует вариантам ответов
            text=option,
            # Присваиваем данные для колбэк запроса.
            # Если ответ верный сформируется колбэк-запрос с данными 'right_answer'
            # Если ответ неверный сформируется колбэк-запрос с данными 'wrong_answer'
            callback_data="right_answer" if option == right_answer else f"wrong_answer:{index}")
        )

    # Выводим по одной кнопке в столбик
    builder.adjust(1)
    return builder.as_markup()

async def get_question(message, user_id):

    # Запрашиваем из базы текущий индекс для вопроса
    current_question_index = await get_quiz_index(user_id)
    # Получаем индекс правильного ответа для текущего вопроса
    correct_index = questions_list[current_question_index]['correct_option']
    # Получаем список вариантов ответа для текущего вопроса
    opts = questions_list[current_question_index]['options']

    # Функция генерации кнопок для текущего вопроса квиза
    # В качестве аргументов передаем варианты ответов и значение правильного ответа (не индекс!)
    kb = generate_options_keyboard(opts, opts[correct_index])
    # Отправляем в чат сообщение с вопросом, прикрепляем сгенерированные кнопки
    await message.answer(f"{questions_list[current_question_index]['question']}", reply_markup=kb)

async def new_quiz(message):
    # получаем id пользователя, отправившего сообщение
    user_id = message.from_user.id
    # сбрасываем значение текущего индекса вопроса квиза в 0
    current_question_index = 0
    await update_quiz_index(user_id, current_question_index)

    # запрашиваем новый вопрос для квиза
    await get_question(message, user_id)

# Хэндлер на команду /start
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    # Создаем сборщика клавиатур типа Reply
    builder = ReplyKeyboardBuilder()
    # Добавляем в сборщик одну кнопку
    builder.add(types.KeyboardButton(text="Начать игру"))
    # Прикрепляем кнопки к сообщению
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))

# Хэндлер на команды /quiz
@router.message(F.text=="Начать игру")
@router.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    # Отправляем новое сообщение без кнопок
    await message.answer(f"Давайте начнем квиз!")
    # Запускаем новый квиз
    await new_quiz(message)

@router.callback_query(F.data == "right_answer")
async def right_answer(callback: types.CallbackQuery):
    # редактируем текущее сообщение с целью убрать кнопки (reply_markup=None)
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    # Получение текущего вопроса для данного пользователя
    current_question_index = await get_quiz_index(callback.from_user.id)

    # Отправляем в чат сообщение, что ответ верный
    await callback.message.answer(f"Ваш ответ: {questions_list[current_question_index]['options'][questions_list[current_question_index]['correct_option']]} - Верно!")

    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)

    # Проверяем достигнут ли конец квиза
    if current_question_index < len(questions_list):
        # Следующий вопрос
        await get_question(callback.message, callback.from_user.id)
    else:
        # Уведомление об окончании квиза
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")

@router.callback_query(F.data.startswith("wrong_answer:"))
async def wrong_answer(callback: types.CallbackQuery):
    # редактируем текущее сообщение с целью убрать кнопки (reply_markup=None)
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    # Извлекаем индекс неправильного ответа из callback_data
    wrong_index = int(callback.data.split(":")[1])

    # Получение текущего вопроса для данного пользователя
    current_question_index = await get_quiz_index(callback.from_user.id)
    correct_option = questions_list[current_question_index]['correct_option']

    # Отправляем в чат сообщение об ошибке с указанием верного ответа
    await callback.message.answer(f"Ваш ответ: {questions_list[current_question_index]['options'][wrong_index]} - Неправильно. Правильный ответ: {questions_list[current_question_index]['options'][correct_option]}")

    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)

    # Проверяем достигнут ли конец квиза
    if current_question_index < len(questions_list):
        # Следующий вопрос
        await get_question(callback.message, callback.from_user.id)
    else:
        # Уведомление об окончании квиза
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")