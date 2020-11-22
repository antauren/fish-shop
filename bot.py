from functools import partial

import redis
from dotenv import dotenv_values
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
                          MessageHandler, Updater)

import elasticpath

_database = None

SEPARATOR = '-(|)-'


def show_product(bot, update, access_token):
    query = update.callback_query

    product = elasticpath.get_product(product_id=query.data, access_token=access_token)['data']

    price_text = '{} {}'.format(product['price'][0]['amount'], product['price'][0]['currency'])

    text = '{}\n\n{}\n{}\n\n{}'.format(
        product['name'],
        price_text,
        product['weight']['kg'],
        product['description'],
    )

    keyboard = [
        [
            InlineKeyboardButton(amount, callback_data=SEPARATOR.join([product['id'], product['name'], str(amount)]))
            for amount in range(1, 6)
        ],
        [
            InlineKeyboardButton('Назад', callback_data='back'),
            InlineKeyboardButton('Корзина', callback_data='cart')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    file_ = elasticpath.get_file(file_id=product['relationships']['main_image']['data']['id'],
                                 access_token=access_token)
    img_url = file_['data']['link']['href']

    bot.send_photo(chat_id=query.message.chat_id, photo=img_url, caption=text, reply_markup=reply_markup)
    bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)

    return 'HANDLE_DESCRIPTION'


def handle_description(bot, update, access_token):
    query = update.callback_query

    product_id, product_name, quantity = query.data.split(SEPARATOR)
    chat_id = query.message.chat_id

    elasticpath.add_product_to_cart(access_token, chat_id, product_id, int(quantity))

    bot.answer_callback_query(callback_query_id=query.id,
                              text='Товар "{}" добавлен в корзину.'.format(product_name),
                              show_alert=False)

    return 'HANDLE_DESCRIPTION'


def show_menu(bot, update, access_token):
    products = elasticpath.get_products(access_token)['data']

    keyboard = [
        [InlineKeyboardButton(product['name'], callback_data=product['id'])]
        for product in products
    ]
    keyboard.append(
        [InlineKeyboardButton('Корзина', callback_data='cart')]
    )
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        bot.sendMessage(chat_id=update.callback_query.message.chat_id,
                        text='Меню:',
                        reply_markup=reply_markup,
                        )
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id,
                           )

    elif update.message:
        update.message.reply_text('Меню:', reply_markup=reply_markup)
        bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

    return 'HANDLE_MENU'


def show_cart(bot, update, access_token):
    query = update.callback_query

    if SEPARATOR in query.data:
        product_id, product_name = query.data.split(SEPARATOR)
        elasticpath.remove_cart_item(query.message.chat_id, product_id, access_token)

        bot.answer_callback_query(callback_query_id=query.id,
                                  text='Товар "{}" удалён из корзины.'.format(product_name),
                                  show_alert=False)

    products = elasticpath.get_cart_items(user=query.message.chat_id, access_token=access_token)

    keyboard = [
        [
            InlineKeyboardButton('Убрать из корзины {}'.format(product['name']),
                                 callback_data=SEPARATOR.join([product['id'], product['name']])
                                 )
        ]
        for product in products['data']
    ]
    keyboard += [
        [InlineKeyboardButton('Оплатить', callback_data='pay')],
        [InlineKeyboardButton('В меню', callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = 'Корзина:\n'
    for product in products['data']:
        formatted_value = product['meta']['display_price']['with_tax']['value']['formatted']
        formatted_unit = product['meta']['display_price']['with_tax']['unit']['formatted']

        text += '\nтовар: {}\nцена: {}\nколичество: {}\nсумма: {}\n'.format(product['name'],
                                                                            formatted_unit,
                                                                            product['quantity'],
                                                                            formatted_value
                                                                            )

    formatted_sum = products['meta']['display_price']['with_tax']['formatted']

    text += '\nИтого: {}'.format(formatted_sum)

    bot.sendMessage(chat_id=query.message.chat_id, text=text, reply_markup=reply_markup)
    bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)

    return 'SHOW_CART'


def send_email(bot, update):
    if update.callback_query.data == 'pay':
        bot.sendMessage(chat_id=update.callback_query.message.chat_id, text='Введите Ваш email:')

    bot.delete_message(chat_id=update.callback_query.message.chat_id,
                       message_id=update.callback_query.message.message_id)

    return 'WAITING_EMAIL'


def waiting_email(bot, update, access_token):
    username = str(update.message.chat.id)
    email = update.message.text

    customers = elasticpath.filter_customers_by_email(email=email, access_token=access_token)

    if not customers['data']:
        elasticpath.create_customer(username=username,
                                    email=email,
                                    access_token=access_token)

    bot.sendMessage(chat_id=update.message.chat.id,
                    text='Ваш заказ зарегестрирован. Менеджер напишет Вам на емейл {} в течение часа.'.format(email))


def handle_users_reply(bot, update, host, port, password, access_token):
    """
    Функция, которая запускается при любом сообщении от пользователя и решает как его обработать.

    Эта функция запускается в ответ на эти действия пользователя:
        * Нажатие на inline-кнопку в боте
        * Отправка сообщения боту
        * Отправка команды боту
    Она получает стейт пользователя из базы данных и запускает соответствующую функцию-обработчик (хэндлер).
    Функция-обработчик возвращает следующее состояние, которое записывается в базу данных.
    Если пользователь только начал пользоваться ботом, Telegram форсит его написать "/start",
    поэтому по этой фразе выставляется стартовое состояние.
    Если пользователь захочет начать общение с ботом заново, он также может воспользоваться этой командой.
    """
    db = get_database_connection(host, port, password)
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return

    if user_reply == '/start':
        user_state = 'SHOW_MENU'
    elif user_reply == 'back':
        user_state = 'SHOW_MENU'
    elif user_reply == 'cart':
        user_state = 'SHOW_CART'
    elif user_reply == 'pay':
        user_state = 'SEND_EMAIL'
    else:
        user_state = db.get(chat_id).decode('utf-8')

    states_functions = {
        'HANDLE_MENU': partial(show_product, access_token=access_token),
        'HANDLE_DESCRIPTION': partial(handle_description, access_token=access_token),
        'SHOW_MENU': partial(show_menu, access_token=access_token),
        'SHOW_CART': partial(show_cart, access_token=access_token),
        'SEND_EMAIL': send_email,
        'WAITING_EMAIL': partial(waiting_email, access_token=access_token),
    }
    state_handler = states_functions[user_state]

    try:
        next_state = state_handler(bot, update)
        db.set(chat_id, next_state)
    except Exception as err:
        print(err)


def get_database_connection(host, port, password):
    """
    Возвращает конекшн с базой данных Redis, либо создаёт новый, если он ещё не создан.
    """
    global _database
    if _database is None:
        _database = redis.Redis(host=host, port=port, password=password)
    return _database


if __name__ == '__main__':
    env_values = dotenv_values()
    client_id = env_values['ELASTICPATH_CLIENT_ID']
    client_secret = env_values['ELASTICPATH_CLIENT_SECRET']

    db_password = env_values['DATABASE_PASSWORD']
    db_host = env_values['DATABASE_HOST']
    db_port = env_values['DATABASE_PORT']

    access_token = elasticpath.get_access_token(client_id, client_secret)

    p_handle_users_reply = partial(handle_users_reply,
                                   host=db_host,
                                   port=db_port,
                                   password=db_password,
                                   access_token=access_token,
                                   )

    token = env_values['TELEGRAM_TOKEN']
    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(p_handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, p_handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', p_handle_users_reply))
    updater.start_polling()
