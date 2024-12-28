import sqlite3
import telebot
import random
import logging
import requests

# Инициализация логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

bot = telebot.TeleBot('7613256994:AAFbcyF3pnuuW4aAl4fZiMYpNKyHXdqvbSI')
API_KEY = '9bbf77f57ccc6526bec4140baee1268a'

# Создание таблицы users, если она не существует
def initialize_db():
    with sqlite3.connect('db.db') as conn:
        cur = conn.cursor()
        cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            pass TEXT NOT NULL DEFAULT 'default_password'
        )
        ''')
        conn.commit()

initialize_db()

# Функция для проверки, зарегистрирован ли пользователь
def is_user_registered(user_id):
    with sqlite3.connect('db.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT id FROM users WHERE id = ?', (user_id,))
        return cur.fetchone() is not None

# Функция для регистрации пользователя
def register_user(user_id, name):
    with sqlite3.connect('db.db') as conn:
        cur = conn.cursor()
        cur.execute('INSERT INTO users (id, name, pass) VALUES (?, ?, ?)', (user_id, name, 'default_password'))
        conn.commit()
    logger.info(f"Пользователь {user_id} ({name}) зарегистрирован.")

# Функция для удаления пользователя
def delete_user(user_id):
    with sqlite3.connect('db.db') as conn:
        cur = conn.cursor()
        cur.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
    logger.info(f"Пользователь {user_id} удалён.")

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if is_user_registered(user_id):
        bot.send_message(message.chat.id, 'Вы уже зарегистрированы! Добро пожаловать снова!')
    else:
        register_user(user_id, message.from_user.first_name)
        bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}! Вы успешно зарегистрированы!')

@bot.message_handler(commands=['delete'])
def delete(message):
    user_id = message.from_user.id
    if is_user_registered(user_id):
        delete_user(user_id)
        bot.send_message(message.chat.id, 'Ваш аккаунт успешно удалён. Вы можете зарегистрироваться заново.')
    else:
        bot.send_message(message.chat.id, 'Ваш аккаунт не найден. Вы не зарегистрированы.')

@bot.message_handler(commands=['build'])
def random_build(message):
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Дешёвый', 'Средний', 'Высокий')

    bot.send_message(message.chat.id, "Какой ПК вы хотите собрать? Выберите одну из категорий:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ['Дешёвый', 'Средний', 'Высокий'])
def build_selection(message):
    category = message.text
    build = get_random_build(category)
    bot.send_message(message.chat.id, f'Вот случайная сборка для категории "{category}":\n{build}')

def get_random_build(category):
    cheap_builds = [
        'Процессор: Intel Pentium G6400\nВидеокарта: GTX 1650\nОперативная память: 8GB DDR4\nЖесткий диск: 500GB HDD',
        'Процессор: AMD Athlon 3000G\nВидеокарта: Vega 3\nОперативная память: 8GB DDR4\nЖесткий диск: 240GB SSD',
        'Процессор: Intel Core i3-10100\nВидеокарта: GTX 1050 Ti\nОперативная память: 8GB DDR4\nЖесткий диск: 1TB HDD'
    ]

    mid_range_builds = [
        'Процессор: AMD Ryzen 5 3600\nВидеокарта: GTX 1660 Ti\nОперативная память: 16GB DDR4\nЖесткий диск: 500GB SSD',
        'Процессор: Intel Core i5-11400\nВидеокарта: RTX 2060\nОперативная память: 16GB DDR4\nЖесткий диск: 1TB SSD',
        'Процессор: AMD Ryzen 7 3700X\nВидеокарта: GTX 1660 Super\nОперативная память: 16GB DDR4\nЖесткий диск: 512GB SSD'
    ]

    high_end_builds = [
        'Процессор: AMD Ryzen 9 7900X\nВидеокарта: RTX 4090\nОперативная память: 32GB DDR5\nЖесткий диск: 1TB NVMe SSD',
        'Процессор: Intel Core i9-13900K\nВидеокарта: RTX 4080\nОперативная память: 32GB DDR5\nЖесткий диск: 2TB NVMe SSD',
        'Процессор: AMD Ryzen 7 5800X3D\nВидеокарта: RTX 3080 Ti\nОперативная память: 32GB DDR4\nЖесткий диск: 1TB NVMe SSD'
    ]

    if category == 'Дешёвый':
        return random.choice(cheap_builds)
    elif category == 'Средний':
        return random.choice(mid_range_builds)
    elif category == 'Высокий':
        return random.choice(high_end_builds)

@bot.message_handler(commands=['info'])
def info(message):
    bot.send_message(
        message.chat.id,
        'Я — бот, который поможет тебе подобрать и приобрести идеальный компьютер под твои нужды! 🚀\n\n'
        '🔧 Сборки ПК на заказ: Мы предлагаем качественные сборки для игр, работы с графикой, видео и 3D моделированием, а также для повседневных задач.\n\n'
        '🖥 Продажа готовых ПК: Если ты не хочешь собирать ПК самостоятельно, у нас есть готовые решения с высококачественными комплектующими.\n\n'
        '💡 Консультации: Не уверен, что выбрать? Могу помочь тебе разобраться в характеристиках и подсказать, какая сборка или комплектующие подойдут именно для тебя.',
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['weather'])
def weather(message):
    bot.send_message(message.chat.id, 'Напиши название города, чтобы узнать погоду.')

@bot.message_handler(func=lambda message: True)
def handle_weather_or_greeting(message):
    city = message.text.strip()
    if city.lower() in ['привет', 'здравствуйте', 'хай']:
        bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}! Чем могу помочь?')
        return

    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather_desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        bot.send_message(
            message.chat.id,
            f'Погода в {city}:\n🌡 Температура: {temp}°C\n☁️ Описание: {weather_desc}'
        )
    elif response.status_code == 401:
        bot.send_message(message.chat.id, "Ошибка: Недействительный API-ключ.")
    else:
        bot.send_message(message.chat.id, "Город не найден. Проверьте название или попробуйте ещё раз.")

bot.polling(none_stop=True)

