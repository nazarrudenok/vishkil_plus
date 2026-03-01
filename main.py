import telebot
import requests
from telebot import types
from config import *

bot = telebot.TeleBot(bot)

def get_pib(message):
    pib = message.text.split(' ')

    params = {
        'name': pib[1],
        'key': '699d6947ec23f92d81c2e392',
    }

    response = requests.get('https://api.genderapi.io/api', params=params)
    sex = response.json()['gender']

    cursor.execute("UPDATE users SET firstname = %s, lastname = %s, sex = %s WHERE username = %s", (pib[1], pib[0], sex, message.from_user.username))
    connection.commit()

    msg = bot.send_message(message.chat.id, 'Далі потрібен твій позивний\nЯкщо ще не маєш позивного напиши «немає»')
    bot.register_next_step_handler(msg, get_poz)

def get_poz(message):
    poz = message.text.lower()

    cursor.execute("UPDATE users SET poz = %s WHERE username = %s", (f'{poz[0].upper()}{poz[1:]}' if poz != 'немає' else '-', message.from_user.username))
    connection.commit()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    button = types.KeyboardButton(text='Надіслати контакт', request_contact=True)
    markup.add(button)

    msg = bot.send_message(message.chat.id, 'Тепер номер телефону. Надішли свій контакт', reply_markup=markup)
    bot.register_next_step_handler(msg, get_num)

def send_adm(message):
    text = message.text

    cursor.execute("SELECT chat_id FROM users")
    ids = cursor.fetchall()

    for i in ids:
        bot.send_message(i['chat_id'], text)

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.username == None:
        bot.send_message(message.chat.id, 'Для продовження роботи додай у налаштуваннях ім\'я користувача. Коли зробиш це - тисни /start')
    else:
        cursor.execute("SELECT * FROM users WHERE username = %s", (message.from_user.username))
        is_exists = cursor.fetchall()
        if is_exists == ():
            cursor.execute("INSERT INTO users (username, chat_id) VALUES (%s, %s)", (message.from_user.username, message.from_user.id))
            connection.commit()
        
            msg = bot.send_message(message.chat.id, 'Вітаю, друже! Ти вже пройшов другий етап відбору. Далі тобі необхідно створити особистий кабінет на порталі Вишкіл+\nНапиши своє прізвище та ім\'я')
            bot.register_next_step_handler(msg, get_pib)
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            b1 = types.KeyboardButton(text='📄 Ваші документи')
            b2 = types.KeyboardButton(text='❓ Часті запитання')
            b3 = types.KeyboardButton(text='💬 Зв\'язок з оперативним черговим')
            markup.add(b1, b2, b3)

            cursor.execute("SELECT * FROM users WHERE username = %s", (message.from_user.username))
            user_data = cursor.fetchone()

            bot.send_message(message.chat.id, f"Вітаю, {user_data['username'] if user_data['username'] != "-" else user_data['firstname']}", reply_markup=markup)

@bot.message_handler(commands=['send'])
def admin(message):
    if message.from_user.id == 8220945297:
        msg = bot.send_message(8220945297, 'Текст:')
        bot.register_next_step_handler(msg, send_adm)

@bot.message_handler(content_types=['contact'])
def get_num(message):
    cursor.execute("UPDATE users SET num = %s WHERE username = %s", (message.contact.phone_number, message.from_user.username))
    connection.commit()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    b1 = types.KeyboardButton(text='📄 Ваші документи')
    b2 = types.KeyboardButton(text='❓ Часті запитання')
    b3 = types.KeyboardButton(text='💬 Зв\'язок з оперативним черговим')
    markup.add(b1, b2, b3)

    cursor.execute("SELECT * FROM users WHERE username = %s", (message.from_user.username))
    user_data = cursor.fetchone()

    msg = bot.send_message(message.chat.id, f"""
<b>Особистий кабінет створено</b>
—————————
Функціонал Вишкіл+ для тебе відкритий.

«📄 Ваші документи»
Тут ти можеш переглянути свої дані (в подальшому тобі буде присвоєно взвод та відділення, слідкуй за повідомленнями).

«❓ Часті запитання»
Для твоєї зручності ти можеш отримати відповіді на найпоширеніші запитання та не чекати довгої відповіді.

«💬 Звʼязок з оперативним черговим»
Якщо ж відповіді на своє запитання ти не знайшов, ти можеш звʼязатися з Оперативним черговим, який вже знає відповіді на будь-які запитання.

Також сюди буде надходити важлива інформація до самого вишколу, тому слідкуй!
""", reply_markup=markup, parse_mode='HTML')
    bot.clear_step_handler(msg)

@bot.message_handler(content_types=['text'])
def text(message):
    if message.text == '📄 Ваші документи':
        cursor.execute("SELECT * FROM users WHERE username = %s", (message.from_user.username))
        user_data = cursor.fetchone()

        text = f"""
<b>Прізвище та ім'я:</b> {user_data['lastname']} {user_data['firstname']}
<b>Позивний:</b> {user_data['poz']}
<b>Взвод:</b> Очікуйте розподіл
<b>Відділення:</b> Очікуйте розподіл
"""
        bot.send_message(message.chat.id, text, parse_mode='HTML')

    elif message.text == '💬 Зв\'язок з оперативним черговим':
        markup = types.InlineKeyboardMarkup()
        b1 = types.InlineKeyboardButton(text='Зв\'язатися', url='https://t.me/Operational_duty_officer_vvl26')
        markup.add(b1)

        bot.send_message(message.chat.id, 'Оперативний черговий на зв\'язку 🟢', reply_markup=markup)

bot.polling()