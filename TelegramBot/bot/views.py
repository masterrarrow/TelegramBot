# from django.shortcuts import render
from django.conf import settings
from random import randint
from django.http import HttpResponse
from django.views import View
from telebot import TeleBot, types, logger
from bot.models import User, Category, Content, Country, Link, User_category, User_content, SentLinks
from threading import Timer
import logging

logger.setLevel(logging.DEBUG)

__author__ = '@masterarrow'

bot = TeleBot(settings.TOKEN)

# region Adjustments

# List of items selected by a user
selected_categories = []
selected_content = []
selected_country = []

# For search content in categories
content = []

usr_categories = []
usr_content = []

# All items in the database
categories = Category.objects.all()
countries = Country.objects.all()
contents = Content.objects.all()

# All category, country and content names
category_name = [cat.name for cat in categories]
country_name = [country.name for country in countries]
content_name = [content.name for content in contents]


# endregion Adjustments


class UpdateBot(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("Бот запущен и работает.")

    def post(self, request, *args, **kwargs):
        # global update_id
        json_str = request.body.decode('UTF-8')
        update = types.Update.de_json(json_str)
        bot.process_new_updates([update])

        return HttpResponse(status=200)


# region START

@bot.message_handler(commands=['start'])
def start_message(message):
    # Start chat with the bot
    bot.delete_message(message.chat.id, message.message_id)
    user = (message.from_user.id, message.from_user.username)

    users = None
    try:
        # Check for user existence in the database
        users = User.objects.get(user_id=f'{user[0]}')
    except:
        pass

    if users:
        # User exists
        show_done(message)
    else:
        # Start adjusting
        usr = User(user_id=f'{user[0]}', name=f'{user[1]}')
        usr.save()

        text = '<b>Настройка рассылки!</b>\n\n'
        text += 'Чтобы получать рассылку интересных каналов, ' \
                'ботов и чатов, настрой параметры.\n\n'
        text += '1. Категории\n\n'
        text += '2. Страна\n\n'
        text += '3. Контент'
        text += '<a href="https://telegra.ph/file/b4012250165f46bbcfafa.jpg">&#160;</a>'

        keyboard = types.InlineKeyboardMarkup()
        key_begin = types.InlineKeyboardButton(
            text='🖊️ Начать', callback_data='begin')
        keyboard.add(key_begin)

        bot.send_message(message.chat.id, text=text,
                         reply_markup=keyboard, parse_mode='HTML')


# endregion START


# region CATEGORY

def show_inline_keyboard(message, items: list, selected_items, call: str, text=None):
    """
        ### Show keyboard

        :param message: telegram message;

        :param items: list of items to show;

        :param selected_items: list of selected items or selected item;

        :param call:  callback_data for confirmation button;

        :param text: displayed message text. Empty means edit previous message
    """
    keyboard = types.InlineKeyboardMarkup()
    buttons = []
    for item in items:
        # If item is selected, mark it
        data = '️️️✔️ ' if item.name in selected_items else ''

        buttons.append(types.InlineKeyboardButton(text=data + item.name,
                                                  callback_data=item.name))

        if len(buttons) == 2:
            # Two buttons in row
            keyboard.add(*buttons)
            buttons.clear()

    if buttons:
        # Add remaining button
        keyboard.add(*buttons)

    key_next = types.InlineKeyboardButton(text='✅️ Готово', callback_data=call)
    keyboard.add(key_next)

    if text:
        bot.send_message(message.chat.id, text=text,
                         reply_markup=keyboard, parse_mode='html')
    else:
        bot.edit_message_reply_markup(message.chat.id, message.message_id,
                                      reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: 'categories' in call.data or 'category' in call.data)
def save_categories(call):
    # Save selected categories to the database
    try:
        # Get user categories from database
        usr = User.objects.get(user_id=f'{call.message.chat.id}')
        user_categories = User_category.objects.filter(user_id__exact=usr)
    except:
        user_categories = []
    values = [i.user_category.name for i in user_categories]

    # Save selected categories to the database
    for data in selected_categories:
        # Add only new items to the database
        if data not in values:
            cat = Category.objects.get(name=data)
            user = User.objects.get(user_id=f'{call.message.chat.id}')
            usr_cat = User_category(user_id=user, user_category=cat)
            usr_cat.save()

    # Delete deselected items from database
    for item in user_categories:
        if item.user_category.name not in selected_categories:
            item.delete()

    bot.delete_message(call.message.chat.id, call.message.message_id)

    if call.data == 'categories':
        show_countries(call.message)


@bot.callback_query_handler(func=lambda call: 'begin' in call.data)
def show_categories(call):
    # Manage categories
    bot.delete_message(call.message.chat.id, call.message.message_id)

    text = '<b>Категории!</b>\n\n'
    text += 'Выбери один или несколько вариантов'
    text += '<a href="https://telegra.ph/file/26ba9528b06f8b231580f.jpg">&#160;</a>'

    # user_categories = None
    global usr_categories
    try:
        # Get user categories
        usr = User.objects.get(user_id=f'{call.message.chat.id}')
        usr_categories = User_category.objects.filter(user_id__exact=usr)
    except:
        usr_categories = []

    callback = 'categories' if len(usr_categories) == 0 else 'category'

    global selected_categories
    selected_categories = [i.user_category.name for i in usr_categories]

    show_inline_keyboard(call.message, categories,
                         selected_categories, callback, text=text)


@bot.callback_query_handler(func=lambda call: call.data in category_name)
def add_category(call):
    # Add selected category to a lit for saving or remove it
    callback = 'categories' if len(usr_categories) == 0 else 'category'
    # bot.delete_message(call.message.chat.id, call.message.message_id)

    # Add selected category to a list
    if call.data not in selected_categories:
        selected_categories.append(call.data)
    else:
        selected_categories.remove(call.data)

    # Mark or remove mark from item
    show_inline_keyboard(call.message, categories,
                         selected_categories, callback)


# endregion CATEGORY


# region COUNTRY

@bot.callback_query_handler(func=lambda call: 'countries' in call.data or 'country' in call.data)
def save_country(call):
    # Save selected country to the database
    if selected_country:
        country = Country.objects.get(name=selected_country[0])
        user = User.objects.get(user_id=f'{call.message.chat.id}')
        user.country = country
        user.save()
    bot.delete_message(call.message.chat.id, call.message.message_id)
    if call.data == 'countries':
        show_content(call.message)


def show_countries(message):
    # Choose country
    text = '<b>Страна!</b>\n\n'
    text += 'Теперь выбери страну в которой проживаешь'
    text += '<a href="https://telegra.ph/file/6e22ac89e8b654b5e7120.jpg">&#160;</a>'

    try:
        # Get user data
        usr = User.objects.get(user_id=f'{message.chat.id}')
        selected_items = usr.country.name
    except:
        usr = User()
        selected_items = []

    callback = 'countries' if not usr.country else 'country'

    show_inline_keyboard(message, countries,
                         selected_items, callback, text=text)


@bot.callback_query_handler(func=lambda call: call.data in country_name)
def add_country(call):
    # Add selected country to a lit for saving or remove it
    usr = User.objects.get(user_id=f'{call.message.chat.id}')
    callback = 'countries' if not usr.country else 'country'
    # Add selected country to a list
    selected_country.clear()
    selected_country.append(call.data)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    # Mark or remove mark from item
    show_inline_keyboard(call.message, countries,
                         selected_country, callback)


# endregion COUNTRY


# region CONTENT

@bot.callback_query_handler(func=lambda call: 'contents' in call.data or 'content' in call.data)
def save_content(call):
    # Save selected content to the database
    try:
        # Get user content
        usr = User.objects.get(user_id=f'{call.message.chat.id}')
        user_content = User_content.objects.filter(user_id__exact=usr)
    except:
        user_content = []
    values = [i.user_content.name for i in user_content]

    # Save selected content to the database
    for data in selected_content:
        # Add only new items to the database
        if data not in values:
            cont = Content.objects.get(name=data)
            user = User.objects.get(user_id=f'{call.message.chat.id}')
            usr_cont = User_content(user_id=user, user_content=cont)
            usr_cont.save()

    # Delete deselected items from database
    for item in user_content:
        if item.user_content.name not in selected_content:
            item.delete()

    bot.delete_message(call.message.chat.id, call.message.message_id)
    if call.data == 'contents':
        show_done(call.message)


def show_content(message):
    # Manage content
    text = '<b>Контент!</b>\n\n'
    text += 'Теперь выбери что именно тебя интересует'
    text += '<a href="https://telegra.ph/file/3351e39357699c056b5a7.jpg">&#160;</a>'

    global usr_content
    try:
        # Get user content
        usr = User.objects.get(user_id=f'{message.chat.id}')
        usr_content = User_content.objects.filter(user_id__exact=usr)
    except:
        usr_content = []

    callback = 'contents' if len(usr_content) == 0 else 'content'

    global selected_content
    selected_content = [i.user_content.name for i in usr_content]

    show_inline_keyboard(
        message, contents, selected_content, callback, text=text)


@bot.callback_query_handler(func=lambda call: call.data in content_name)
def add_content(call):
    # Add selected country to a lit for saving or remove it from a list
    callback = 'contents' if len(usr_content) == 0 else 'content'
    bot.delete_message(call.message.chat.id, call.message.message_id)

    # Add selected content to a list
    if call.data not in selected_content:
        selected_content.append(call.data)
    else:
        selected_content.remove(call.data)

    # Mark or remove mark from item
    show_inline_keyboard(call.message, contents,
                         selected_content, callback)


# endregion CONTENT


# region DONE

def show_done(message):
    # All adjustments are done
    text = '<b>Ты настроил рассылку!</b>\n\n'
    text += 'Теперь я буду присылать тебе интересный контент. '
    text += 'Также ты можешь искать его самостоятельно, для этого жми кнопку "Поиск"'
    text += '<a href="https://telegra.ph/file/d7af54ad265f953943a6d.jpg">&#160;</a>'

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row('📬 Рассказать друзьям')
    markup.row('Поиск')
    markup.row('Настроить интересы')
    bot.register_next_step_handler(message, menu)

    bot.send_message(message.chat.id, text=text,
                     reply_markup=markup, parse_mode='HTML')


# endregion DONE


# region MANAGE INTERESTS

def menu(message):
    # Manage responses from ReplyKeyboardMarkup
    try:
        # Always working ???
        if message.text == '📬 Рассказать друзьям':
            # Share with friends
            markup = types.InlineKeyboardMarkup()
            forward_btn = types.InlineKeyboardButton(
                text='📱 Пригласить друга',
                url='https://t.me/share/url?url=https://t.me/' + bot.get_me().username)
            markup.add(forward_btn)
            text = 'С моей помощью ты можешь искать интересные каналы, ' \
                   'боты, чаты, исключительно '
            text += 'по своим интересам. Также можешь настроить рассылку и ' \
                    'я буду присылать тебе по твоим интересам.'
            text += '<a href="https://telegra.ph/file/520c703b1cba3810caa03.jpg">&#160;</a>'
            bot.send_message(message.chat.id, text=text,
                             reply_markup=markup, parse_mode='html')
            bot.register_next_step_handler(message, menu)

        elif message.text == 'Поиск':
            bot.delete_message(message.chat.id, message.message_id)
            # Search in the selected categories
            markup = types.InlineKeyboardMarkup()
            search_channel = types.InlineKeyboardButton(
                text='Каналы', callback_data='search_Каналы')
            search_bot = types.InlineKeyboardButton(
                text='Боты', callback_data='search_Боты')
            search_chat = types.InlineKeyboardButton(
                text='Чаты', callback_data='search_Чаты')
            markup.row(search_channel)
            markup.row(search_bot)
            markup.row(search_chat)
            text = '<b>Что искать?</b>'
            text += '<a href="https://telegra.ph/file/62fb9b93b09020d3af35c.jpg">&#160;</a>'
            bot.send_message(message.chat.id, text=text,
                             parse_mode='html', reply_markup=markup)
            bot.register_next_step_handler(message, menu)

        elif message.text == 'Настроить интересы':
            # Manage interests
            manage_interests(message)
            bot.register_next_step_handler(message, menu)

        else:
            raise Exception()
    except:
        bot.register_next_step_handler(message, menu)


def manage_interests(message):
    # Change interests
    try:
        usr = User.objects.get(user_id=f'{message.chat.id}')
        # Get user categories
        cat = User_category.objects.filter(user_id__exact=usr)
        # Get user content
        cont = User_content.objects.filter(user_id__exact=usr)

        usr_category = [i.user_category.name for i in cat]
        usr_cont = [i.user_content.name for i in cont]
    except:
        usr = User()
        usr_category = []
        usr_cont = []

    usr_category = ', '.join(usr_category)
    usr_cont = ', '.join(usr_cont)

    text = '<b>Настроить интересы!</b>\n\n'
    text += 'Смена интересов приведет к смене рассылки\n'
    text += f'1. Категории: {usr_category}\n'
    text += f'2. Страна: {usr.country.name}\n'
    text += f'3. Контент: {usr_cont}'
    text += '<a href="https://telegra.ph/file/02be4d5254d3f032360fd.jpg">&#160;</a>'

    keyboard = types.InlineKeyboardMarkup()
    key_1 = types.InlineKeyboardButton(
        text='1. Категории', callback_data='begin')  # show_categories
    key_2 = types.InlineKeyboardButton(
        text='2. Страна', callback_data='categories')  # show_countries
    key_3 = types.InlineKeyboardButton(
        text='3. Контент', callback_data='countries')  # show_content
    keyboard.add(key_1)
    keyboard.add(key_2)
    keyboard.add(key_3)

    bot.send_message(message.chat.id, text=text,
                     reply_markup=keyboard, parse_mode='html')


# endregion MANAGE INTERESTS


# region SEARCH FOR CHANNELS

@bot.inline_handler(func=lambda query: len(query.query) > 0)
def show_links(query):
    # Go to selected a category in channels (Inline mode)
    # (to register handler: In botFather /setinline, choose bot and enter hint text)
    name, data = query.query.split('_')
    try:
        # Get links for user categories and content
        cont = Content.objects.get(name=name)
        cat = Category.objects.get(name=data)
        links = Link.objects.filter(
            content__exact=cont).filter(category__exact=cat)
    except:
        links = []

    if links:
        results = []
        i = 0
        # Show data in inline mode
        for link in links:
            # Show categories
            back_btn = types.InlineKeyboardButton(
                text='Назад', callback_data='search_' + name)
            # Show channel (use https://bitly.com to track link's clicks)
            button = types.InlineKeyboardButton(text='Перейти', url=f'{link.link}')

            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(back_btn, button)

            # Message text
            text = f'<b>{link.name}</b>\n'
            text += f'<a href="{link.image_link}">&#160;</a>'

            msg = types.InlineQueryResultArticle(
                id=f'{i}', title=f'{link.name}', description=f'{link.date}\n{link.description}',
                input_message_content=types.InputTextMessageContent(
                    message_text=text, parse_mode='html'),
                reply_markup=keyboard
            )
            results.append(msg)
            i += 1

        bot.answer_inline_query(query.id, results)


@bot.callback_query_handler(func=lambda call: 'back' in call.data)
def del_msg(call):
    # Delete previous message
    bot.delete_message(call.message.chat.id, call.message.message_id)


@bot.callback_query_handler(
    func=lambda call: 'search_Каналы' in call.data or 'search_Боты' in call.data or 'search_Чаты' in call.data)
def search_channels(call):
    # Search in channels
    text = '<b>Поиск!</b>\n\n'
    text += 'Выбирай категорию и ищи интересный контент'
    text += '<a href="https://telegra.ph/file/62fb9b93b09020d3af35c.jpg">&#160;</a>'

    """
    # Show only user categories
    global usr_categories
    try:
        # Get user categories and content
        usr = User.objects.get(user_id=f'{call.message.chat.id}')
        usr_categories = User_category.objects.filter(user_id__exact=usr)
    except:
        usr_categories = []

    chat_id = call.message.chat.id if call.message else call.from_user.id
    show_buttons(chat_id, text, 'Каналы_', usr_categories)
    """

    # Show all categories
    _, data = call.data.split('_')
    chat_id = call.message.chat.id if call.message else call.from_user.id
    show_buttons(chat_id, text, data + '_', categories)


def show_buttons(chat_id, text, prefix, items):
    """
        ### Show buttons for searched categories

        :param chat_id: chat id;

        :param text: Text for displaying;

        :param prefix: prefix for switch_inline_query_current_chat;

        :param items: list of items for displaying
    """
    keyboard = types.InlineKeyboardMarkup()
    key_back = types.InlineKeyboardButton(
        text='◀️ Назад', callback_data='back')
    keyboard.add(key_back)

    buttons = []
    for item in items:
        # Add items for search
        # item.user_category.name - for user categories
        # item.name - for all categories
        content.append(prefix + item.name)
        # Add button for each category
        buttons.append(
            types.InlineKeyboardButton(text=item.name,
                                       switch_inline_query_current_chat=prefix + item.name))

        if len(buttons) == 2:
            # Two buttons in row
            keyboard.add(*buttons)
            buttons.clear()

    if buttons:
        # Add remaining button
        keyboard.add(*buttons)

    bot.send_message(chat_id, text=text, reply_markup=keyboard, parse_mode='html')


# endregion SEARCH FOR CHANNELS


# region NEWSLETTER

def send_newsletter(user_id: int, text: str, link: str):
    # Send newsletter to a user
    keyboard = types.InlineKeyboardMarkup()
    # (use https://bitly.com to track link's clicks)
    keyboard.add(types.InlineKeyboardButton(text='Перейти', url=f'{link}'))

    bot.send_message(user_id, text=text,
                     reply_markup=keyboard, parse_mode='html')


def newsletter():
    # Start timer for sending newsletter (duration is in seconds)
    # Send two links per day
    update_thread = Timer(60 * 60 * 12, send_data())
    update_thread.start()


def send_data():
    # Send random link two times per day for all users
    try:
        # Get all users from the database
        users = User.objects.all()
    except:
        users = []

    for user in users:
        try:
            # Get data
            user_category = User_category.objects.filter(user_id__exact=user)
            user_content = User_content.objects.filter(user_id__exact=user)
            sent_links = SentLinks.objects.filter(user__exact=user)
            # List of links sent to a user
            links_list = [sent_link.link for sent_link in sent_links]

            choose = True
            while choose:
                # Choose random indices
                cont_ind = randint(0, len(user_content) - 1)
                cat_ind = randint(0, len(user_category) - 1)
                current_cont = user_content[cont_ind]
                current_cat = user_category[cat_ind]
                # Get links for channels
                links = Link.objects.filter(content__exact=current_cont.user_content).filter(
                    category__exact=current_cat.user_category)
                if len(links) != 0:
                    index = randint(0, len(links) - 1)
                    link = links[index]
                    # Link was not send to a user
                    if link not in links_list:
                        # Message text
                        text = f'<b>{link.name}</b>\n'
                        text += f'<a href="{link.image_link}">&#160;</a>'
                        # Add link to the database
                        new_link = SentLinks(user=user, link=link)
                        new_link.save()

                        # Send message to a user
                        send_newsletter(user_id=user.user_id, text=text, link=link.link)
                        # Stop
                        choose = False
        except:
            pass


# Start newsletter
newsletter()

# endregion NEWSLETTER

# Not available in release mode.
if settings.DEBUG:
    # Start polling in another thread
    # (allows not to freeze django admin)
    bot.remove_webhook()
    from threading import Thread

    t1 = Thread(target=bot.polling)
    t1.start()
else:
    bot.remove_webhook()
    bot.set_webhook(url=f"{settings.DOMAIN}/{settings.TOKEN}")

