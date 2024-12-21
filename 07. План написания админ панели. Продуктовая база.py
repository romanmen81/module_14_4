from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from crud_functions import initiate_db, get_all_products
from aiogram import types
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Определяем класс состояний
class UserState(StatesGroup):
    age = State()     # Состояние для ввода возраста
    growth = State()  # Состояние для ввода роста
    weight = State()  # Состояние для ввода веса

# Инициализация бота и диспетчера
bot = Bot(token='7542914141:AAEGE-IRdCWrwjhrFbppasBq6gmTKcU707w')  # Замените YOUR_BOT_TOKEN на ваш токен
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Создание основной клавиатуры
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
button_start = KeyboardButton('Начать')  # Кнопка "Начать"
button_calculate = KeyboardButton('Рассчитать')
button_info = KeyboardButton('Информация')
button_buy = KeyboardButton('Купить')  # Кнопка "Купить"
keyboard.add(button_start, button_calculate, button_info, button_buy)

# Создание Inline клавиатуры для расчета и формул
inline_keyboard = InlineKeyboardMarkup()
button_calories = InlineKeyboardButton('Рассчитать норму калорий', callback_data='calories')
button_formulas = InlineKeyboardButton('Формулы расчёта', callback_data='formulas')
inline_keyboard.add(button_calories, button_formulas)

# Создание Inline клавиатуры для продуктов
product_inline_keyboard = InlineKeyboardMarkup()
button_product1 = InlineKeyboardButton('Product1', callback_data='product_buying')
button_product2 = InlineKeyboardButton('Product2', callback_data='product_buying')
button_product3 = InlineKeyboardButton('Product3', callback_data='product_buying')
button_product4 = InlineKeyboardButton('Product4', callback_data='product_buying')
product_inline_keyboard.add(button_product1, button_product2, button_product3, button_product4)

# Функция для старта бота
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Привет! Я бот, помогающий твоему здоровью.", reply_markup=keyboard)

# Обработка нажатия кнопки "Начать"
@dp.message_handler(lambda message: message.text == 'Начать')
async def restart_bot(message: types.Message):
    await start(message)

# Функция для главного меню (Inline клавиатура)
@dp.message_handler(lambda message: message.text == 'Рассчитать')
async def main_menu(message: types.Message):
    await message.answer('Выберите опцию:', reply_markup=inline_keyboard)

# Функция для получения формул
@dp.callback_query_handler(lambda call: call.data == 'formulas')
async def get_formulas(call: types.CallbackQuery):
    await call.answer()  # Подтверждаем нажатие кнопки
    await call.message.answer('Формула Миффлина-Сан Жеора для мужчин:\n'
                              'Калории = 10 * вес + 6.25 * рост - 5 * возраст + 5')

# Функция для получения возраста
@dp.callback_query_handler(lambda call: call.data == 'calories')
async def set_age(call: types.CallbackQuery):
    await call.answer()  # Подтверждаем нажатие кнопки
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()  # Установка состояния age

# Функция для получения роста
@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)  # Сохранение возраста
    await message.answer('Введите свой рост:')
    await UserState.growth.set()  # Установка состояния growth

# Функция для получения веса
@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    await state.update_data(growth=message.text)  # Сохранение роста
    await message.answer('Введите свой вес:')
    await UserState.weight.set()  # Установка состояния weight

# Функция для вычисления нормы калорий
@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    await state.update_data(weight=message.text)  # Сохранение веса
    data = await state.get_data()  # Получение всех данных
    age = int(data['age'])  # Извлечение возраста
    growth = int(data['growth'])  # Извлечение роста
    weight = int(data['weight'])  # Извлечение веса

    # Формула Миффлина - Сан Жеора (для мужчин)
    calories = 10 * weight + 6.25 * growth - 5 * age + 5

    await message.answer(f'Ваша норма калорий: {calories} калорий в день.')  # Ответ пользователю
    await state.finish()  # Завершение состояния


# Импортируем необходимые модули и функции
from crud_functions import get_all_products
from aiogram import types
import os


@dp.message_handler(lambda message: message.text == 'Купить')
async def get_buying_list(message: types.Message):
    # Получаем список продуктов из базы данных
    products = get_all_products()

    # Перебираем продукты и отправляем сообщения
    for product in products:
        product_id = product[0]
        product_title = product[1]
        product_description = product[2]
        product_price = product[3]

        image_path = f"{product_title}.jpg"  # Формируем путь к изображению

        await message.answer(
            f'Название: {product_title} | Описание: {product_description} | Цена: {product_price} рублей'
        )
        with open(image_path, 'rb') as img:
            await message.answer_photo(photo=img)

    await message.answer('Выберите продукт для покупки:', reply_markup=product_inline_keyboard)

# Функция для подтверждения покупки
@dp.callback_query_handler(lambda call: call.data == 'product_buying')
async def send_confirm_message(call: types.CallbackQuery):
    await call.answer()  # Подтверждаем нажатие кнопки
    await call.message.answer("Вы успешно приобрели продукт!")

# Запуск бота
async def on_startup(dp):
    logging.info('Бот запущен!')

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)