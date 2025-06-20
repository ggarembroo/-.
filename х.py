import telebot
from telebot import types
import smtplib
from email.mime.text import MIMEText
import os

bot = telebot.TeleBot("")

user_data = {}
ceiling_photos = {
    "grilliato_24": "https://zpk-ermak.ru/thumb/2/Ha-GbyePiXy5NWdwCtiA6A/r/d/gl24.jpg",
    "grilliato_15": "https://zpk-ermak.ru/thumb/2/q1TH5WZ2qUGCb752X_0aMw/r/d/gl15.jpg",
    "grilliato_10": "https://zpk-ermak.ru/d/grilyatozh4.jpg",
    "cubic_reyka": "https://zpk-ermak.ru/d/kafe.jpg",
    "cassette_ceiling": "https://zpk-ermak.ru/d/kassetapotolok.jpg",
    "cube_3d": "https://zpk-ermak.ru/d/f3-2var2.jpg",
    "magnit_stena": "https://zpk-ermak.ru/thumb/2/VkWyCSLAPD9JFvyZo_yqlQ/r/d/magnitstena2.jpg"
}

# Функция для отправки email
def send_email(user_data):
    sender_email =""  #тут короче нужна почта на которую будет приходить сообщения, пожайлуста ничего не трогайте
    sender_password = "" #так как у меня не было почты я вписал свою, это пароль, замените на другую
    receiver_email = ""

    message = MIMEText(f"Новый клиент!\nИмя: {user_data.get('name', 'Не указано')}\nТип потолка: {user_data['ceiling_type']}\nПлощадь: {user_data['area']}\nКонтакт: {user_data['contact']}")
    message['Subject'] = "Новый клиент Telegram бота!"
    message['From'] = sender_email
    message['To'] = receiver_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email отправлен")
    except Exception as e:
        print(f"Ошибка отправки email: {e}")

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    # Удаляем предыдущее сообщение с кнопками
    bot.delete_message(call.message.chat.id, call.message.message_id)

    # Обработка нажатий на кнопки с типами потолков
    if call.data in ceiling_photos:
        photo_id = ceiling_photos[call.data]
        bot.send_photo(call.message.chat.id, photo_id, caption=f"Фото {call.data}")

    # Запрос квадратуры после выбора типа потолка
    if call.data in ["grilliato_24", "grilliato_15", "grilliato_10", "cubic_reyka", "cassette_ceiling", "cube_3d"]:
        bot.send_message(call.message.chat.id, "Как к вам обращаться?")
        bot.register_next_step_handler(call.message, process_name, call.data)

    # Возврат в главное меню
    elif call.data == "back_to_main":
        main(call.message)

def process_name(message, ceiling_type):
    # Сохраняем имя пользователя
    name = message.text
    user_id = message.chat.id
    user_data[user_id] = {'ceiling_type': ceiling_type, 'name': name}

    # Запрашиваем квадратуру
    bot.send_message(message.chat.id, "Какая у вас квадратура?")
    bot.register_next_step_handler(message, process_area, ceiling_type)

def process_area(message, ceiling_type):
    # Обработка введенной площади
    try:
        area = float(message.text)
        user_id = message.chat.id
        user_data[user_id]['area'] = area
        bot.send_message(message.chat.id, f"Площадь: {area}. Теперь укажите ваш номер телефона или email для связи:")
        bot.register_next_step_handler(message, process_contact)
    except ValueError:
        bot.send_message(message.chat.id, "Некорректный ввод. Введите число (площадь).")

def process_contact(message):
    # Обработка контактных данных
    contact = message.text
    user_id = message.chat.id
    user_data[user_id]['contact'] = contact
    bot.send_message(message.chat.id, f"Спасибо! Мы свяжемся с вами в ближайшее время. Ваш контакт: {contact}")

    # Отправка данных на email
    send_email(user_data[user_id])

@bot.message_handler(content_types=['photo', 'video'])
def process_file(message):
    # Обработка фото и видео (просто вывод file_id в консоль)
    file_id = message.photo[-1].file_id if message.photo else message.video.file_id
    file_type = 'photo' if message.photo else 'video'
    print(f'Обрабатываю {file_type}: {file_id}')

@bot.message_handler(commands=['start'])
def main(message):
    # Главное меню
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Потолки")
    item2 = types.KeyboardButton("Рассчитать площадь")
    item3 = types.KeyboardButton("Рассчитать периметр")
    keyboard.add(item1, item2, item3)
    bot.send_message(message.chat.id, "Здравствуйте, какой потолок хотели бы Вы приобрести?", reply_markup=keyboard)

# Обработчик нажатия на кнопку "Потолки"
@bot.message_handler(func=lambda message: message.text == "Потолки")
def ceilings_menu(message):
    #Меню выбора типов потолков
    keyboard = types.InlineKeyboardMarkup()
    key_grilliato_10 = types.InlineKeyboardButton(text='Грильято_10', callback_data='grilliato_10')
    key_grilliato_15 = types.InlineKeyboardButton(text='Грильято_15', callback_data='grilliato_15')
    key_grilliato_24 = types.InlineKeyboardButton(text='Грильято_24', callback_data='grilliato_24')
    key_cubic_reyka = types.InlineKeyboardButton(text='Кубическая рейка', callback_data='cubic_reyka')
    key_cassette_ceiling = types.InlineKeyboardButton(text='Кассетный потолок', callback_data='cassette_ceiling')
    key_cube_3d = types.InlineKeyboardButton(text='КУБ 3D', callback_data='cube_3d')
    key_magnit_stena = types.InlineKeyboardButton(text='магнитная стена ', callback_data='magnit_stena')
    key_back = types.InlineKeyboardButton(text='Назад', callback_data='back_to_main') # Кнопка "Назад"
    keyboard.add(key_grilliato_15)
    keyboard.add(key_magnit_stena)
    keyboard.add(key_grilliato_24)
    keyboard.add(key_grilliato_10)
    keyboard.add(key_cubic_reyka)
    keyboard.add(key_cassette_ceiling)
    keyboard.add(key_cube_3d)
    keyboard.add(key_back)
    bot.send_message(message.chat.id, text='Выберите тип потолка:', reply_markup=keyboard)

# Обработчик нажатия на кнопку "Рассчитать площадь" умру скоро
@bot.message_handler(func=lambda message: message.text == "Рассчитать площадь")
def calculate_area(message):
    # Меню выбора типа расчета площади
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Площадь")
    item2 = types.KeyboardButton("Общая площадь")
    back_button = types.KeyboardButton("Назад в главное меню") # Кнопка "Назад"
    keyboard.add(item1, item2, back_button)
    bot.send_message(message.chat.id, "Выберите, что вы хотите рассчитать:", reply_markup=keyboard)

# Обработчик для расчета площади (одной)
@bot.message_handler(func=lambda message: message.text == "Площадь")
def calculate_single_area(message):
    # Запрос длины и ширины для расчета площади
    bot.send_message(message.chat.id, "Введите длину и ширину через пробел (например, 5 4):")
    bot.register_next_step_handler(message, process_area_calculation)

def process_area_calculation(message):
    # Обработка введенных данных и расчет площади
    try:
        length, width = map(float, message.text.split())
        area = length * width
        bot.send_message(message.chat.id, f"Площадь: {area}")
    except ValueError:  #отсеить хитрожопых
        bot.send_message(message.chat.id, "Некорректный ввод. Пожалуйста, введите два числа через пробел.")

# Обработчик для расчета общей площади
@bot.message_handler(func=lambda message: message.text == "Общая площадь")
def calculate_total_area(message):
    # Запрос площадей для расчета общей площади
    bot.send_message(message.chat.id, "Введите площади через пробел (например, 10 20 30):")
    bot.register_next_step_handler(message, process_total_area_calculation)

def process_total_area_calculation(message):
    # Обработка введенных данных и расчет общей площади
    try:
        areas = map(float, message.text.split())
        total_area = sum(areas)
        bot.send_message(message.chat.id, f"Общая площадь: {total_area}")
    except ValueError:
        bot.send_message(message.chat.id, "Некорректный ввод. Пожалуйста, введите числа через пробел.")

# Обработчик для расчета периметра
@bot.message_handler(func=lambda message: message.text == "Рассчитать периметр")
def calculate_perimeter(message):
    # Запрос длины и ширины для расчета периметра
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back_button = types.KeyboardButton("Назад в главное меню") # Кнопка "Назад"
    keyboard.add(back_button)
    bot.send_message(message.chat.id, "Введите длину и ширину через пробел (например, 5 4):", reply_markup=keyboard)
    bot.register_next_step_handler(message, process_perimeter_calculation)

def process_perimeter_calculation(message):
    # Обработка введенных данных и расчет периметра
    try:
        length, width = map(float, message.text.split())
        perimeter = 2 * (length + width)
        bot.send_message(message.chat.id, f"Периметр: {perimeter}")
    except ValueError:
        bot.send_message(message.chat.id, "Некорректный ввод. Пожалуйста, введите два числа через пробел.")

# Обработчик команды /help
@bot.message_handler(commands=['help'])
def help_info(message):
    # Вывод справочной информации
    bot.send_message(message.chat.id, "Команды: /start, /help")

# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    # Обработка текстовых сообщений (приветствия и команды help)
    if message.text.lower() == 'привет':
        bot.send_message(message.chat.id, "Здравствуйте, какой бы потолок хотели бы Вы приобрести?")
    elif    message.text.lower() == 'здравствуйте':
        bot.send_message(message.chat.id, "Здравствуйте, какой бы потолок хотели бы Вы приобрести?")
    elif message.text.lower() == 'хай':
        bot.send_message(message.chat.id, "Здравствуйте, какой бы потолок хотели бы Вы приобрести?")
    elif message.text.lower() == 'help':
        bot.reply_to(message, 'Команды: /start, /help')
    elif message.text == "Назад в главное меню":
        main(message)

bot.polling(non_stop=True) #усе PS. если import os не работает то опустите на 1 строку ниже!!!
