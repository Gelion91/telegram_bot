import re
from glob import glob
from random import choice
import logging
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
import ephem
import datetime
import city
from emoji import emojize

import settings


logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log')


def get_keyboard():
    contact_button = KeyboardButton('Прислать контакты', request_contact=True)
    location_button = KeyboardButton('Прислать координаты', request_location=True)
    start_keyboard = ReplyKeyboardMarkup([
        ['Покажи мне все!'], [contact_button, location_button]
    ], resize_keyboard=True, one_time_keyboard=True)
    return start_keyboard


reply_keyboard = [
    ['Поиграть в города', 'Когда полнолуние', 'Количество слов'], ['Все команды', 'Прислать котика', 'Сменить аватар']
]
keyboard = ReplyKeyboardMarkup(reply_keyboard,resize_keyboard=True, one_time_keyboard=False)
exit_keyboard = ReplyKeyboardMarkup([['выход']], resize_keyboard=True, one_time_keyboard=True)

YOUR_TURN, ANSWER, COUNT = range(3)


def greet_user(update, context):
    user_data = context.user_data
    emo = get_user_emo(user_data)
    user_data['emo'] = emo
    text = 'Привет {}'.format(emo)
    update.message.reply_text(text, reply_markup=get_keyboard())


def get_contact(update, context):
    user_data = context.user_data
    print(update.message.contact)
    update.message.reply_text('Спасибо {}'.format(get_user_emo(user_data)))


def get_location(update, context):
    user_data = context.user_data
    print(update.message.location)
    update.message.reply_text('Спасибо {}'.format(get_user_emo(user_data)))


def get_user_emo(user_data):
    if 'emo' in user_data:
        return user_data['emo']
    else:
        user_data['emo'] = emojize(choice(settings.USER_EMOJI), use_aliases=True)
        return user_data['emo']


def change(update, context):
    user_data = context.user_data
    if 'emo' in user_data:
        del user_data['emo']
        emo = get_user_emo(user_data)
        update.message.reply_text('Готово! {}'.format(emo))


def send_cat(update, context):
    cat_list = glob('images/cat*.jp*g')
    cat_pic = choice(cat_list)
    context.bot.send_photo(chat_id=update.message.chat_id, photo=open(cat_pic, 'rb'))


def planet_info(update, context):
    """Принимает команду от пользователя и выводит результат о местонахождении планеты"""

    your_question = update.message.text.split()
    quest = getattr(ephem, your_question[-1])
    constellation = ephem.constellation(quest(datetime.date.today()))
    update.message.reply_text(f'Сегодня {your_question[-1]} находится в созведии {constellation[-1]}')


def help_list(update, context):
    """Выводит список доступных команд"""
    for i in ephem._libastro.builtin_planets():
        if 'Planet' in i:
            update.message.reply_text('/planet ' + i[-1])
    text = '''  /next_full_moon - что бы узнать когда ближайшее полнолуние.
    /wordcount <text> что бы узнать количество слов в веденном тексте.'''
    update.message.reply_text(text)


def counter(update, context):
    update.message.reply_text('Введите предложение в котором надо посчитать слова.')
    return COUNT


def numbers(update, context):
    """ Выводит количество слов """
    user_text = re.sub(r"[,./_()""*:;]", "", update.message.text)
    format_text = user_text.split()
    print(format_text)
    logging.info('Message: %s', update.message.text)
    update.message.reply_text(len(format_text))
    return YOUR_TURN


def full_moon(update, context):
    """ Выводит ближайшее полнолуние """
    answer = ephem.next_full_moon(datetime.date.today())
    update.message.reply_text(answer)


def start(update, context):
    user_data = context.user_data
    emo = get_user_emo(user_data)
    """ Открывает клавиатуру с выбором команды """
    update.message.reply_text('Привет! Что бы ты хотел сделать? {}'.format(emo), reply_markup=keyboard)
    return YOUR_TURN


def cities(update, context):
    """ Стартует игру в города"""
    update.message.reply_text('Твой ход!', reply_markup=exit_keyboard)
    user_data = context.user_data
    user_data['city'] = []
    user_data['count'] = 0
    return ANSWER


def received_information(update, context):
    """ Основное тело игры """
    text = update.message.text
    user_data = context.user_data
    user_data['count'] += 1
    if text == 'выход':
        update.message.reply_text("Пока играли, были названы города: {}".format(user_data['city']))
        user_data['city'].clear()
        return ConversationHandler.END
    if text not in user_data['city'] and \
            (user_data['count'] < 2 or text[0].lower() == user_data['city'][-1].strip('ьый')[-1]) and \
            text in city.russian_cities:
        user_data.setdefault('city', []).append(text)
        update.message.reply_text("Да город {} есть!".format(text))
        text = text.rstrip('ьый')
        for name in city.russian_cities:
            if name[0].lower() != text[-1] or name in user_data['city']:
                continue
            else:
                update.message.reply_text(f'Тааак... мне город на {text[-1]}\nО! Придумал: {name}')
                user_data['city'].append(name)
            break
    else:
        update.message.reply_text("Давай играть по правилам!!!")


def main():
    """Тело бота"""
    mybot = Updater(settings.API_KEY, request_kwargs=settings.PROXY, use_context=True)
    logging.info('Бот запускается')
    dp = mybot.dispatcher
    dp.add_handler(CommandHandler('planet', planet_info, pass_user_data=True))
    dp.add_handler(CommandHandler('wordcount', counter, pass_user_data=True))
    dp.add_handler(CommandHandler('next_full_moon', full_moon, pass_user_data=True))
    dp.add_handler(ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('^Покажи мне все!$'), start, pass_user_data=True)],

        states={
            YOUR_TURN: [MessageHandler(Filters.regex('Поиграть в города'), cities, pass_user_data=True),
                        MessageHandler(Filters.regex('Когда полнолуние'), full_moon, pass_user_data=True),
                        MessageHandler(Filters.regex('Количество слов'), counter, pass_user_data=True),
                        MessageHandler(Filters.regex('Все команды'), help_list, pass_user_data=True),
                        MessageHandler(Filters.regex('^(Прислать котика)$'), send_cat, pass_user_data=True),
                        MessageHandler(Filters.regex('^(Сменить аватар)$'), change, pass_user_data=True)],
            ANSWER: ([MessageHandler(Filters.text, received_information, pass_user_data=True)]),
            COUNT: ([MessageHandler(Filters.text, numbers, pass_user_data=True)])
        },
        fallbacks=[])
    )
    dp.add_handler(MessageHandler(Filters.text, greet_user, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.contact, get_contact, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.location, get_location, pass_user_data=True))
    mybot.start_polling()
    mybot.idle()


main()
