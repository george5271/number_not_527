import telebot
from telebot import types
import binary_config

bot = telebot.TeleBot(binary_config.TOKEN)



@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, f'Hi, {message.from_user.first_name}'
                                      f'\nI\'m George\'s first Bot, nice to see you here.')

    bot.send_sticker(message.chat.id, binary_config.start_sticker)


@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id, binary_config.help_rules)


@bot.message_handler(commands=['get_example'])
def give_example(message):
    bot.send_message(message.chat.id, 'Here is your example:')
    bot.send_photo(message.chat.id, photo=open('example_for_bot.png', 'rb'))


@bot.message_handler(commands=['additional'])
def add(message):
    bot.send_message(message.chat.id, "You can also type me 'hi' or 'hello', 'i luv u' or 'I LOVE YOU' and 'bye' in ANY"
                                      " case and get some phrases from me.")
default_global_dict = {'left_index' : 0, 'right_index': 100, 'count' : 0}



@bot.message_handler(commands=['play'])
def play_game(message):
    user_session = get_session(message)
    reset_session(user_session)
    send_response(message, user_session)


def send_response(message, user_session):
    keyboard = types.InlineKeyboardMarkup()  # Adding keyboard
    key_less = types.InlineKeyboardButton(text='-', callback_data='less')
    key_more = types.InlineKeyboardButton(text='+', callback_data='more')
    key_equal = types.InlineKeyboardButton(text='=', callback_data='equal')
    keyboard.add(key_equal, key_less, key_more)
    user_session['count'] += 1
    bot.send_message(message.chat.id,
                     f"Is your number: {(user_session['left_index'] + user_session['right_index']) // 2}?",
                     reply_markup=keyboard)


def get_session(message):
    user_id = message.from_user.id
    if user_id in users:
        user_session = users[user_id]
    else:
        user_session = {'user_id' : user_id, 'username' : message.from_user.first_name}
        users[user_id] = user_session
        user_session['chat_id'] = message.chat.id
        user_session['chat_username'] = message.chat.username
        reset_session(user_session)
    return user_session


def reset_session(user_session):
    user_session['left_index'] = 0
    user_session['right_index'] = 100
    user_session['count'] = 0


@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    message = call.message
    user_session = get_session(call)
    centre_index = (user_session['left_index'] + user_session['right_index']) // 2
    user_session['current_centre'] = centre_index

    if call.data == 'equal':
        bot.send_message(call.message.chat.id, f"Bot guessed your number: {centre_index}")
        user_session['left_index'], user_session['right_index'], user_session['count'] = 2, 100, 0

    else:
        if call.data == 'less':
            print(user_session)  # Отладка
            user_session['right_index'] = centre_index - 1
            # send_response(message, user_session)

        elif call.data == 'more':
            print(user_session)  # Отладка
            user_session['left_index'] = centre_index + 1
            # send_response(message, user_session)

        if user_session['left_index'] > user_session['right_index']:
            bot.send_message(call.message.chat.id, 'Придурь, играй нормально, меня не обманишь!\n'
                                                   "\nYou can play again, just type '/' and choose 'play'")
        else:
            send_response(message, user_session)




@bot.message_handler(content_types=['text'])
def get_text(message):
    if message.text.lower() == 'hi' or message.text.lower() == 'hello':
        bot.send_message(message.chat.id, f'Hi, {message.from_user.username}👋')
        bot.send_sticker(message.chat.id, binary_config.hello_sticker)

    elif message.text.lower() == 'i luv u' or message.text.lower() == 'i love you':
        bot.send_message(message.chat.id, 'Me too, human')
        bot.send_sticker(message.chat.id, binary_config.love_sticker)

    elif message.text.lower() == 'bye':
        bot.send_message(message.chat.id, f'See you soon, {message.from_user.username}')
        bot.send_sticker(message.chat.id, binary_config.bye_sticker)
    else:
        bot.send_message(message.chat.id, 'i can\'t get you, type /start or /help for more info')


bot.polling(none_stop=True, interval=0)
