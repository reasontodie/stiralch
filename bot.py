# -*- coding: cp1251 -*-
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

bot_token = 'TOKEN'
bot = telebot.TeleBot(bot_token)

# Список пользователей, которые записались на стирку
queue = []

# Словарь пользователей, которые начали стирку
active_users = {}
# Список администраторов
admins = [459642118]

# Обработчик команды /start для администраторов
@bot.message_handler(commands=['newgenbabyy'])
def start_command_admin(message):
    if message.chat.id in admins:
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        queue_btn = telebot.types.KeyboardButton('Записаться на стирку')
        view_queue_btn = telebot.types.KeyboardButton('Очередь')
        cancel_btn = telebot.types.KeyboardButton('Отменить запись на стирку')
        done_btn = telebot.types.KeyboardButton('Я достирал')
        delete_user_btn = telebot.types.KeyboardButton('Удалить пользователя')
        move_user_btn = telebot.types.KeyboardButton('Переместить пользователя')
        report_btn = telebot.types.KeyboardButton('Сообщить об ошибке')
        own_queue_btn = telebot.types.KeyboardButton('Own очередь')
        markup.row(queue_btn, view_queue_btn)
        markup.row(cancel_btn, done_btn)
        markup.row(own_queue_btn, move_user_btn)
        markup.row(report_btn)
        bot.reply_to(message, "Привет, администратор! Чем я могу помочь?", reply_markup=markup)
    else:
        bot.reply_to(message, "Извините, вы не являетесь администратором.")

# Обработчик кнопки 'Удалить пользователя'
@bot.message_handler(func=lambda message: message.text == 'Удалить пользователя')
def delete_user_command(message):
    if message.chat.id in admins:
        bot.reply_to(message, "Введите номер пользователя в очереди, которого необходимо удалить:")
        bot.register_next_step_handler(message, process_delete_user)
    else:
        bot.reply_to(message, "Извините, вы не являетесь администратором.")

#Админская очередь
@bot.message_handler(func=lambda message: message.text == 'Own очередь' and message.chat.id in admins)
def own_view_queue_command(message):
    if len(queue) > 0:
        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        for i, user_id in enumerate(queue):
            username = bot.get_chat_member(message.chat.id, user_id).user.username
            button = telebot.types.InlineKeyboardButton(text=f"{i+1}. @{username} - Удалить", callback_data=f"delete_user {user_id}")
            markup.add(button)
        bot.reply_to(message, "Очередь на стирку:", reply_markup=markup)
    else:
        bot.reply_to(message, "Очередь на стирку пуста.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_user'))
def delete_user_callback(call):
        user_id = int(call.data.split()[1])
        if user_id in queue:
            queue.remove(user_id)
            bot.answer_callback_query(call.id, text="Пользователь удален из очереди.")
            update_queue()
        else:
            bot.answer_callback_query(call.id, text="Пользователь не найден в очереди.")



# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_command(message):
    if message.chat.id in admins:
        start_command_admin(message)
    else:
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        queue_btn = telebot.types.KeyboardButton('Записаться на стирку')
        view_queue_btn = telebot.types.KeyboardButton('Очередь')
        cancel_btn = telebot.types.KeyboardButton('Отменить запись на стирку')
        done_btn = telebot.types.KeyboardButton('Я достирал')
        report_btn = telebot.types.KeyboardButton('Сообщить об ошибке')
        markup.row(queue_btn, view_queue_btn)
        markup.row(cancel_btn, done_btn)
        markup.row(report_btn)
        bot.reply_to(message, "Привет! Этот бот поможет тебе записаться на стирку и следить за очередью.", reply_markup=markup)

# Обработчик кнопки 'Записаться на стирку'
@bot.message_handler(func=lambda message: message.text == 'Записаться на стирку')
def queue_command(message):
    if message.chat.id in queue:
        bot.reply_to(message, f"{message.from_user.first_name}, ты уже записан на стирку.")
    else:
        queue.append(message.chat.id)
        active_users[message.chat.id] = message.from_user.first_name
        bot.reply_to(message, f"{message.from_user.first_name}, ты успешно записался на стирку.")
        update_queue()

# Обработчик кнопки 'Я достирал'
@bot.message_handler(func=lambda message: message.text == 'Я достирал')
def done_command(message):
    if message.chat.id in active_users:
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        yes_btn = KeyboardButton('Да')
        no_btn = KeyboardButton('Нет')
        markup.add(yes_btn, no_btn)
        bot.reply_to(message, f"{message.from_user.first_name}, ты уверен, что достирал и хочешь удалить свою запись?", reply_markup=markup)
        process_done_command_step(message)
    else:
        bot.reply_to(message, f"{message.from_user.first_name}, ты не записан на стирку или уже достирал.")
            
def process_done_command_step(message):
    if message.text == 'Да':
        if message.chat.id in active_users:
            del active_users[message.chat.id]
            queue.remove(message.chat.id)
            bot.reply_to(message, f"{message.from_user.first_name}, спасибо, что позаботился об очереди.")
            update_queue()
            start_command(message)
        else:
            bot.reply_to(message, f"{message.from_user.first_name}, твоя запись на стирку не удалена.")


@bot.message_handler(func=lambda message: message.text == 'Отменить запись на стирку')
def cancel_command(message):
    if message.chat.id in queue:
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        yes_btn = KeyboardButton('Да')
        no_btn = KeyboardButton('Нет')
        markup.add(yes_btn, no_btn)
        bot.reply_to(message, f"{message.from_user.first_name}, ты уверен, что хочешь отменить свою запись на стирку?", reply_markup=markup)
    else:
        bot.reply_to(message, f"{message.from_user.first_name}, ты не записан на стирку.")

# Обработчик кнопок подтверждения отмены записи
@bot.message_handler(func=lambda message: message.text in ['Да', 'Нет'] and message.chat.id in queue)
def cancel_confirm_command(message):
    if message.text == 'Да':
        if message.chat.id in active_users:
            del active_users[message.chat.id]
        queue.remove(message.chat.id)
        bot.reply_to(message, f"{message.from_user.first_name}, твоя запись на стирку отменена.")
        update_queue()
        process_cancel_command_step(message)
    else:
        bot.reply_to(message, f"{message.from_user.first_name}, твоя запись на стирку не отменена.")
        process_cancel_command_step(message)
        
def process_cancel_command_step(message):
    if message.chat.id in admins:
        start_command_admin(message)
    else:
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        queue_btn = telebot.types.KeyboardButton('Записаться на стирку')
        view_queue_btn = telebot.types.KeyboardButton('Очередь')
        cancel_btn = telebot.types.KeyboardButton('Отменить запись на стирку')
        done_btn = telebot.types.KeyboardButton('Я достирал')
        markup.row(queue_btn, view_queue_btn)
        markup.row(cancel_btn)
        bot.send_message(message.chat.id, "Какие еще действия тебе нужны?", reply_markup=markup)

# Обработчик кнопки 'Сообщить об ошибке'
@bot.message_handler(func=lambda message: message.text == 'Сообщить об ошибке')
def report_error_command(message):
        bot.reply_to(message, "Введите сообщение об ошибке:")
        bot.register_next_step_handler(message, process_error_report)

def process_error_report(message):
    error_message = message.text
    bot.send_message(admins[0], f"Сообщение об ошибке от @{message.from_user.username}: {error_message}")
    bot.reply_to(message, "Ваше сообщение было отправлено администратору.")

# Обработчик кнопки 'Очередь'
@bot.message_handler(func=lambda message: message.text == 'Очередь')


# Обновление списка очереди и оповещение пользователей в групповом чате
def update_queue():
    if len(queue) > 0:
        queue_text = "\n".join([f"{i+1}. @{bot.get_chat_member(-1001703606698, user_id).user.username}" for i, user_id in enumerate(queue)])
        bot.send_message(-1001703606698, f"Очередь на стирку:\n{queue_text}")
    else:
        bot.send_message(-1001703606698, f"В очереди никого нету, либо последний человек достирал :)")

def view_queue_command(message):
    chat_id = message.chat.id
    queue = get_queue(chat_id)
    if not queue:
        bot.send_message(chat_id, "Очередь пуста.")
        return
    queue_text = "\n".join([f"{i+1}. @{bot.get_chat_member(chat_id, user_id).user.username}" for i, user_id in enumerate(queue)])
    bot.send_message(chat_id, queue_text)

bot.polling()
