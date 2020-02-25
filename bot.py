import re

from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import logging
import settings
import ephem
import datetime
import city

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log')

reply_keyboard = [['Поиграть в города'],['Когда полнолуние'], ['Количество слов'], ['Все команды']]
keyboard = ReplyKeyboardMarkup(reply_keyboard,resize_keyboard=True, one_time_keyboard=False)
exit_keyboard = ReplyKeyboardMarkup([['выход']], resize_keyboard=True, one_time_keyboard=True)

YOUR_TURN, ANSWER, COUNT = range(3)


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
    """ Открывает клавиатуру с выбором команды """
    update.message.reply_text('Привет! Что бы ты хотел сделать?', reply_markup=keyboard)
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
        user_data.clear()
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
    dp.add_handler(CommandHandler('planet', planet_info))
    dp.add_handler(CommandHandler('wordcount', counter))
    dp.add_handler(CommandHandler('next_full_moon', full_moon))
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            YOUR_TURN: [MessageHandler(Filters.regex('Поиграть в города'), cities),
                        MessageHandler(Filters.regex('Когда полнолуние'), full_moon),
                        MessageHandler(Filters.regex('Количество слов'), counter),
                        MessageHandler(Filters.regex('Все команды'), help_list)],
            ANSWER: ([MessageHandler(Filters.text, received_information)]),
            COUNT: ([MessageHandler(Filters.text, numbers)])
        },
        fallbacks=[])
    )
    mybot.start_polling()
    mybot.idle()


main()
