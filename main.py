import telebot
import requests
from telebot import types
from openpyxl import Workbook
import os
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
    cursor.execute("SELECT chat_id FROM users")
    ids = cursor.fetchall()

    for i in ids:
        try:
            # Текст
            if message.content_type == 'text':
                bot.send_message(i['chat_id'], message.text)

            # Документ (файл)
            elif message.content_type == 'document':
                file_id = message.document.file_id
                bot.send_document(i['chat_id'], file_id, caption=message.caption)

            # Фото
            elif message.content_type == 'photo':
                file_id = message.photo[-1].file_id
                bot.send_photo(i['chat_id'], file_id, caption=message.caption)

            # Відео (як бонус)
            elif message.content_type == 'video':
                file_id = message.video.file_id
                bot.send_video(i['chat_id'], file_id, caption=message.caption)

        except Exception as e:
            print(f"Помилка при відправці {i['chat_id']}: {e}")

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

            msg = bot.send_message(message.chat.id, 'Вітаю! Ти вже пройшов відбір на «Вишкіл Військового Лідерства 2026». Далі тобі необхідно створити особистий кабінет на порталі Вишкіл+\nНапиши своє прізвище та ім\'я')
            bot.register_next_step_handler(msg, get_pib)
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            b1 = types.KeyboardButton(text='📄 Ваші документи')
            b2 = types.KeyboardButton(text='❓ Часті запитання')
            b3 = types.KeyboardButton(text='👕 Необхідні речі')
            b4 = types.KeyboardButton(text='💬 Зв\'язок з черговим')
            markup.add(b1, b2, b3, b4)

            cursor.execute("SELECT * FROM users WHERE username = %s", (message.from_user.username))
            user_data = cursor.fetchone()

            bot.send_message(message.chat.id, f"Вітаю, {user_data['username'] if user_data['username'] != "-" else user_data['firstname']}", reply_markup=markup)

@bot.message_handler(commands=['send'])
def admin(message):
    if message.from_user.id == 8220945297:
        msg = bot.send_message(message.chat.id, 'Надішли текст або файл:')
        bot.register_next_step_handler(msg, send_adm)

@bot.message_handler(commands=['get_users'])
def get_users(message):
    cursor.execute("SELECT * FROM users")
    data = cursor.fetchall()

    wb = Workbook()
    ws = wb.active

    if data:
        headers = data[0].keys()
        ws.append(list(headers))

        for row in data:
            ws.append(list(row.values()))

    file_name = "users.xlsx"
    wb.save(file_name)

    with open(file_name, "rb") as f:
        bot.send_document(message.chat.id, f)

    os.remove(file_name)

@bot.message_handler(content_types=['contact'])
def get_num(message):
    if message.text:
        msg = bot.send_message(message.chat.id, 'Натисни на кнопку внизу, щоб поділитись контактом')
        bot.register_next_step_handler(msg, get_num)
    else:
        cursor.execute("UPDATE users SET num = %s WHERE username = %s", (message.contact.phone_number, message.from_user.username))
        connection.commit()

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        b1 = types.KeyboardButton(text='📄 Ваші документи')
        b2 = types.KeyboardButton(text='❓ Часті запитання')
        b3 = types.KeyboardButton(text='👕 Необхідні речі')
        b4 = types.KeyboardButton(text='💬 Зв\'язок з черговим')
        markup.add(b1, b2, b3, b4)

        msg = bot.send_message(message.chat.id, f"""
    <b>Особистий кабінет створено</b>
    ——————
    Функціонал Вишкіл+ для тебе відкритий.

    «📄 Ваші документи»
    Тут ти можеш переглянути свої дані (в подальшому тобі буде присвоєно взвод та відділення, слідкуй за повідомленнями).

    «❓ Часті запитання»
    Для твоєї зручності ти можеш отримати відповіді на найпоширеніші запитання та не чекати довгої відповіді.

    «💬 Звʼязок з оперативним черговим»
    Якщо ж відповіді на своє запитання ти не знайшов, ти можеш звʼязатися з Оперативним черговим, який вже знає відповіді на будь-які запитання.

    Також сюди буде надходити важлива інформація до самого вишколу, тому слідкуй!
                            
    <a href='https://t.me/+KKxOOylk0cs0YmNi'>Також приєднюйся до групи з учасниками для комунікації</a>
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

    elif message.text == '💬 Зв\'язок з черговим':
        markup = types.InlineKeyboardMarkup()
        b1 = types.InlineKeyboardButton(text='Зв\'язатися', url='https://t.me/Operational_duty_officer_vvl26')
        markup.add(b1)

        bot.send_message(message.chat.id, 'Оперативний черговий на зв\'язку 🟢', reply_markup=markup)

    elif message.text == '❓ Часті запитання':
        text = """
<b>1. Вишкіл в будні дні, я пропускаю уроки, що робити?</b>
- В заклад освіти, де ви навчаєтесь буде направлено наказ про вашу залученість на вишколі, проблем не буде через пропуск уроків.
<b>2. Чи буде опалення в приміщенні?</b>
- Так, будівля в якій ви будете проживати має опалення.
<b>3. Чи є звʼязок на місці проведення вишколу?</b>
- Так, звʼязок є.
<b>4. Що брати їсти?</b>
- Забезпечується повне харчування впровож всіх 4 днів - 3 рази на день (сніданок, обід, вечеря). Додатково з собою можна взяти ще щось для перекусу або додаткового прийому їжі. Також обовʼязково з собою потрібно мати свою ложку/вилку, тарілку і горнятко, для прийомів їжі поза їдальньою.
<b>5. Чи треба платити?</b>
- Ні, вишкіл проводиться повністю на безоплатній основі, від вас потрібен лише бажання та гарний настрій)
<b>6. Чи обовʼязково мати військову форму?</b>
- Ні, не обовʼязково, достатньо просто зручного одягу, в якому буде комфортно виконувати різноманітні задачі. Проте не варто забувати про демаскуючу властивість військової форми)
<b>7. Там буде де зарядитись?</b>
- Так, в корпусі був ремонт, розеток побільшало, проте переноска лишньою також не буде.
<b>8. Чи буде де помитись?</b>
- Так, в корпусі є душові, на 1 поверсі чоловічі, на 2 жіночі. Також в програмі вишколу закладений час для процедур перед сном, тому з цим не буде жодних проблем.
<b>9. Які будуть особливості виконання місій?</b>
- У нічний час дозволено буде використовувати лише ліхтарі з червоним світлом, тому потрібно мати для себе один.
<b>10. Маю особисте спорядження (броня, рація, підсумки..), чи можна взяти його?</b>
- Так, можна, для вас це буде набагато зручніше.
"""

        bot.send_message(message.chat.id, text, parse_mode='HTML')
    elif message.text == '👕 Необхідні речі':
        text = """
Список необхідних речей (спорядження) для Вишколу Військового лідерства 2026
З огляду на військово-патріотичний характер вишколу, акцент робиться на функціональності, надійності та захисті від погодних умов.

🥾 Тактичне взуття (черевики) – 2 пари: одна основна, одна запасна. Розношена, не нова!

🧦 Шкарпетки – не менше 5 пар: теплі (трекінгові/вовняні) та звичайні.

👖 Комплект польової форми – 2 комплекти (кітель, штани).

🧤 Рукавиці – 2 пари: теплі та робочі/тактичні.

🧢 Головний убір – шапка та/або балаклава, кепка.

🧥 Теплий одяг – термобілизна (верх і низ), флісова кофта (обов'язково!).

🌧 Захист від дощу – якісний дощовик або мембранна куртка/штани.

🎒 Рюкзак – місткий, зручний, припасований.

🛏️ Спальний мішок 

🖱️ Каремат (пінка) – товстий, надійний.

🔦 Ліхтарик – налобний, з червоним світлофільтром і комплектом запасних батарейок.

🧼 Засоби гігієни – зубна щітка, паста, мило, рушник (бажано мікрофібра).

🔥 Засоби для розпалювання вогню – запальничка/сірники, сухе пальне.

💧 Пляшка для води

📱 Павербанк та кабель для зарядки телефону (телефон використовуватиметься мінімально, лише для зв'язку).

✍️ Блокнот та ручка у водонепроникному чохлі (або олівець)

📻 В процесі завданнь будуть використовуватися рації, тому підсумок під неї лишнім не буде. Або ж якщо є особисті рації, теж можна взяти для зручності.

🍽️ Також підготуйте комплект посуду: тарілка, ложка, горнятко.
Можуть бути пластикові, металеві, але не скляні або глиняні.

Всім учасникам необхідно мати плитоноску/бронежилет(можна взяти свої) з підсумками(обов'язково аптечка з тренувальним турнікетом ), РПС та наколінники за бажанням, щоб отримати це спорядження можна звернутись до своїх ЦНПВ, у випадку, якщо з таким майном будуть проблеми, прохання написати в чаті.
"""

        bot.send_message(message.chat.id, text)

bot.polling()