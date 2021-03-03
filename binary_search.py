import telebot
from telebot import types
import binary_config

bot = telebot.TeleBot(binary_config.TOKEN)


@bot.message_handler(commands=['start'])  # Start command handler - Greeting
def start_command(message):
    bot.send_message(message.chat.id, f'Hi, {message.from_user.first_name}'
                                      f'\nI\'m George\'s first Bot, nice to see you here.')

    bot.send_sticker(message.chat.id, binary_config.start_sticker)


@bot.message_handler(commands=['help'])  # Help command handler - gives rules of the game
def help_command(message):
    bot.send_message(message.chat.id, binary_config.help_rules)


@bot.message_handler(commands=['get_example'])  # Get_example command handler - gives photo of example how to play
def give_example(message):
    bot.send_message(message.chat.id, 'Here is your example:')
    bot.send_photo(message.chat.id, photo=open('example_for_bot.png', 'rb'))


@bot.message_handler(
    commands=['additional'])  # Gives user an information about bot\'s abilities (user can type smth and
# bot will answer this)
def add(message):
    bot.send_message(message.chat.id, "You can also type me 'hi' or 'hello', 'i luv u' or 'I LOVE YOU' and 'bye' in ANY"
                                      " case and get some phrases from me.")


gen_stat_list = {'good_gen_games': 0, 'dirt_gen_games': 0, 'gen_game_count': 0}  # Dict with general statistics data


# (initially all values are 0)


@bot.message_handler(commands=['statistics'])  # The beginning of statistics command, more below
def stats_1(message):
    stats_keyboard = types.InlineKeyboardMarkup()  # Adding a kb with buttons: My, General.
    my_stats = types.InlineKeyboardButton(text='My', callback_data='my')
    general_stats = types.InlineKeyboardButton(text='General', callback_data='general')
    stats_keyboard.add(my_stats, general_stats)
    bot.send_message(message.chat.id, 'Choose a kind of statistic you want to see:',
                     reply_markup=stats_keyboard)  # Redirecting to next menu


users = {}  # Dict with users sessions(to have an possibility more than one user can play with bot correctly)


@bot.message_handler(commands=['play'])
def play_game(message):
    user_session = get_session(message)  # Making a session for user
    user_session['active_play'] = True
    gen_stat_list['gen_game_count'] += 1  # Updating current variables
    user_session['user_game_count'] += 1

    reset_session(user_session)  # Reseting current coordinates of searching a number(Initially - L 0, R 100)
    send_response(message, user_session)  # Sending bot\'s calculated number on checking and getting user answer


def get_session(message):
    user_id = message.from_user.id  # Getting user ID

    if user_id in users:  # If user's already played, just getting and waking up an old session
        user_session = users[user_id]

    else:  # If user has never played yet, editing a new session
        user_session = {'user_id': user_id, 'username': message.from_user.first_name,
                        'good_user_games': 0, 'dirt_user_games': 0,
                        'user_game_count': 0,
                        'active_play': False}  # Добавил хорошо и плохо сыгранные игры, и вообще все игры (Статистика
        # только этого пользователя)
        users[user_id] = user_session  # And adding to users
    return user_session


def reset_session(user_session):  # Reseting user session(By adding left and right indexes if they weren`t yet
    # and updating them, if they already were.)
    user_session['left_index'] = 0
    user_session['right_index'] = 100


def send_response(message, user_session):  # Sending bot\'s calculated number on checking and getting user answer
    user_sign_kb = types.InlineKeyboardMarkup()

    key_less = types.InlineKeyboardButton(text='-', callback_data='less')
    key_more = types.InlineKeyboardButton(text='+', callback_data='more')
    key_equal = types.InlineKeyboardButton(text='=', callback_data='equal')

    user_sign_kb.add(key_less, key_more, key_equal)

    bot.send_message(message.chat.id, "Is your number: "
                                      f"{(user_session['left_index'] + user_session['right_index']) // 2}?",
                     reply_markup=user_sign_kb)


call_variants = ['less', 'more', 'equal']


# Call can be only of of them to get inside this query handler (idk why, but this and


# handler below are unable to work together.)


@bot.callback_query_handler(func=lambda call: call.data in call_variants)
def answer(call):
    user_session = get_session(call)
    if not user_session['active_play']:
        return
    message = call.message
    centre_index = (user_session['left_index'] + user_session['right_index']) // 2

    if call.data == 'equal':
        bot.send_message(message.chat.id, f'Bot guessed your number: {centre_index}')
        bot.send_message(message.chat.id, 'Thank you for playing!')
        user_session['good_user_games'] += 1  # Добавляется хорошо сыгранная игра в счетчик пользователя
        gen_stat_list['good_gen_games'] += 1
        user_session['active_play'] = False

    else:  # If user's answer != '='(equal)
        if call.data == 'less':
            user_session['right_index'] = centre_index - 1

        elif call.data == 'more':
            user_session['left_index'] = centre_index + 1

        if user_session['left_index'] > user_session['right_index']:  # If user cheated under bot
            bot.send_message(call.message.chat.id, 'Придурь, играй нормально, меня не обмануть!\n'
                                                   "\nYou can play again, just type '/' and choose 'play'")
            user_session['dirt_user_games'] += 1  # Добавляется плохо сыгранная игра в счетчик пользователя
            gen_stat_list['dirt_gen_games'] += 1
            user_session['active_play'] = False

        else:
            send_response(message, user_session)


value_dict = {}  # Dict for good, dirt and count values(users and general together)


@bot.callback_query_handler(func=lambda call: True)
def stats2(call):
    user_session = get_session(call)
    message = call.message
    mainmenu = types.InlineKeyboardButton(text='◀️Go back', callback_data='back')

    if call.data == 'my':  # If user chose 'My' in first menu
        my_keyboard = types.InlineKeyboardMarkup()
        # Making a keyboard for second menu(user statistic)
        my_good = types.InlineKeyboardButton(text='Good games', callback_data='good_user_games')
        my_bad = types.InlineKeyboardButton(text='Bad games', callback_data='dirt_user_games')
        my_everything = types.InlineKeyboardButton(text='All your games', callback_data='user_game_count')
        my_all_stat = types.InlineKeyboardButton(text='Full story of yours', callback_data='user_full_stat')

        my_keyboard.add(my_good, my_bad, my_everything, row_width=2)
        my_keyboard.add(my_all_stat, mainmenu, row_width=1)

        my_list_buttons = [my_good, my_bad,
                           my_everything]  # Adding text and value for output in scheme text: callback_data (now only
        # for user statistic)
        for button in my_list_buttons:
            value_dict[button.callback_data] = [button.text,
                                                user_session[button.callback_data]
                                                ]
        # Make a separated dict for my_all_stat and gen_all_stat to pull them then in stats3...
        # UPD: completed, but not completed

        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                              # transforming first menu into second user menu
                              text='Choose a type of statistic:', reply_markup=my_keyboard)

    elif call.data == 'general':  # If user chose 'General' in first menu
        gen_keyboard = types.InlineKeyboardMarkup()
        # Making a keyboard for second menu(general statistic)
        gen_good = types.InlineKeyboardButton(text='Well-played games', callback_data='good_gen_games')
        gen_dirt = types.InlineKeyboardButton(text='Dirt-played games', callback_data='dirt_gen_games')
        gen_all = types.InlineKeyboardButton(text='All played games', callback_data='gen_game_count')
        gen_all_stat = types.InlineKeyboardButton(text='Full general statistic', callback_data='gen_full_stat')

        gen_keyboard.add(gen_good, gen_dirt, gen_all, row_width=2)
        gen_keyboard.add(gen_all_stat, mainmenu, row_width=1)

        gen_list_buttons = [gen_good, gen_dirt,
                            gen_all]  # Adding text and value for output in scheme text: callback_data (now already
        # for general statistic too)
        for button in gen_list_buttons:
            value_dict[button.callback_data] = [button.text,
                                                gen_stat_list[button.callback_data]
                                                ]

        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                              text=' Choose the type of statistic:', reply_markup=gen_keyboard)

    elif call.data in value_dict.keys():  # If user entered the second menu and chose good, bad or all games stat to see
        mainmenu_keyboard = types.InlineKeyboardMarkup()  # Keyboard to get into first(initial) menu
        mainmenu_keyboard.add(mainmenu)

        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=
        f'<em>{value_dict[call.data][0]}:</em>  <code>{value_dict[call.data][1]}</code>',
                              parse_mode='HTML',
                              reply_markup=mainmenu_keyboard)  # Added back button(to get into 1st menu)

    elif call.data == 'back':  # One command for getting into 1st menu for three cases above(they have the same button)
        stats_keyboard = types.InlineKeyboardMarkup()

        my_stats = types.InlineKeyboardButton(text='My', callback_data='my')  # the initial(1st) menu
        general_stats = types.InlineKeyboardButton(text='General', callback_data='general')

        stats_keyboard.add(my_stats, general_stats)
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                              text='Choose a kind of statistic you want to see:',
                              reply_markup=stats_keyboard)

    elif call.data == 'user_full_stat':  # Show all user's statistic history
        my_previous_menu = types.InlineKeyboardMarkup()
        my_backwards = types.InlineKeyboardButton(text='◀️Back', callback_data='my_back')
        my_previous_menu.add(my_backwards)
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=
        f'<b>Full story of yours</b>\n'
        f'<pre>Good games:      {user_session["good_user_games"]}\n'
        f'Bad games:       {user_session["dirt_user_games"]}\n'
        f'All your games:  {user_session["user_game_count"]}</pre>',
                              parse_mode='HTML', reply_markup=my_previous_menu)

    elif call.data == 'my_back':
        my_keyboard = types.InlineKeyboardMarkup()
        # Adding a keyboard for second menu(user statistic) AGAIN - to get it, if user presses BACK button
        my_good = types.InlineKeyboardButton(text='Good games', callback_data='good_user_games')
        my_bad = types.InlineKeyboardButton(text='Bad games', callback_data='dirt_user_games')
        my_everything = types.InlineKeyboardButton(text='All your games', callback_data='user_game_count')
        my_all_stat = types.InlineKeyboardButton(text='Full story of yours', callback_data='user_full_stat')

        my_keyboard.add(my_good, my_bad, my_everything, row_width=2)
        my_keyboard.add(my_all_stat, mainmenu, row_width=1)

        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                              text='Choose a type of statistic:', reply_markup=my_keyboard)

    elif call.data == 'gen_full_stat':  # Show all general statistic history
        gen_previous_menu = types.InlineKeyboardMarkup()
        gen_backwards = types.InlineKeyboardButton(text='◀️Back', callback_data='gen_back')
        gen_previous_menu.add(gen_backwards)

        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=
        "<em>Full general statistic</em>\n"
        f"<pre>All good games:   {gen_stat_list['good_gen_games']}\n"
        f"All dirt games:   {gen_stat_list['dirt_gen_games']}\n"
        f"Games in general: {gen_stat_list['gen_game_count']}</pre>",
                              parse_mode='HTML', reply_markup=gen_previous_menu)

    elif call.data == 'gen_back':
        gen_keyboard = types.InlineKeyboardMarkup()
        # Adding a keyboard for second menu(user statistic) AGAIN - to get it, if user presses BACK button
        gen_good = types.InlineKeyboardButton(text='Well-played games', callback_data='good_gen_games')
        gen_dirt = types.InlineKeyboardButton(text='Dirt-played games', callback_data='dirt_gen_games')
        gen_all = types.InlineKeyboardButton(text='All played games', callback_data='gen_game_count')
        gen_all_stat = types.InlineKeyboardButton(text='Full general statistic', callback_data='gen_full_stat')

        gen_keyboard.add(gen_good, gen_dirt, gen_all, row_width=2)
        gen_keyboard.add(gen_all_stat, mainmenu, row_width=1)

        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                              text=' Choose the type of statistic:', reply_markup=gen_keyboard)


@bot.message_handler(content_types=['text'])  # Bot processes another variants of text, user can send
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
        bot.send_message(message.chat.id, 'i can\'t get you, type /start or /help for more info',
                         reply_to_message_id=message.message_id)


bot.polling(none_stop=True, interval=0)