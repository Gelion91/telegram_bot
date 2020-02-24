import re
import time
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from threading import Thread
import logging
import settings
import ephem
import datetime
import city

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log')


def greet_user(bot, update):
    """комманда /start приветствует пользователя"""

    text = 'Добро пожаловать!\n/list - список доступных комманд'
    logging.info(text)
    update.message.reply_text(text)


def talk_to_me(bot, update):
    """обрабатывает неизвестные команды
    сохраняет в bot.log данные о пользователе."""

    user_text = 'Привет! Введите /start или /planet <Название планеты>'
    logging.info('User: %s, chat id: %s, Message: %s',
                 update.message.chat.username,
                 update.message.chat.id,
                 update.message.text
                 )
    update.message.reply_text(user_text)
    update.message.reply_text('/list - список доступных комманд')


def planet_info(bot, update):
    """Принимает команду от пользователя и выводит результат о местонахождении планеты"""

    your_question = update.message.text.split()
    quest = getattr(ephem, your_question[-1])
    constellation = ephem.constellation(quest(datetime.date.today()))
    update.message.reply_text(f'Сегодня {your_question[-1]} находится в созведии {constellation[-1]}')


def list_planet(bot, update):
    """Выводит список доступных команд"""
    for i in ephem._libastro.builtin_planets():
        if 'Planet' in i:
            update.message.reply_text('/planet ' + i[-1])
    text = '''  /next_full_moon - что бы узнать когда ближайшее полнолуние.
    /wordcount <text> что бы узнать количество слов в веденном тексте.'''
    update.message.reply_text(text)


def counter(bot, update):
    """ Выводит количество слов """
    user_text = re.sub(r"[,./_()""*:;]", "", update.message.text)
    format_text = user_text.split()
    print(format_text)
    logging.info('Message: %s', update.message.text)
    update.message.reply_text(len(format_text)-1)


def full_moon(bot, update):
    answer = ephem.next_full_moon(datetime.date.today())
    update.message.reply_text(answer)


def cities(bot, update):
    with open('users.txt', 'r+', encoding='utf-8') as file:
        content = file.read()
        if str(update.message.chat.id) not in content:
            file.write(str(update.message.chat.id) + '\n')
    user_text = update.message.text.split()
    print(update.message)
    text = user_text[-1]
    print(text)
    print(user_text)
    if text in city.russian_cities:
        city.russian_cities.remove(text)
    for name in city.russian_cities:
        if name[0].lower() == text[-1]:
            update.message.reply_text(name)
            city.russian_cities.remove(name)
        else:
            continue
        break


def main():
    """Тело бота"""
    mybot = Updater(settings.API_KEY, request_kwargs=settings.PROXY)
    logging.info('Бот запускается')
    dp = mybot.dispatcher
    dp.add_handler(CommandHandler('start', greet_user))
    dp.add_handler(CommandHandler('planet', planet_info))
    dp.add_handler(CommandHandler('list', list_planet))
    dp.add_handler(CommandHandler('wordcount', counter))
    dp.add_handler(CommandHandler('next_full_moon', full_moon))
    dp.add_handler(CommandHandler('cities', cities))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))
    mybot.start_polling()
    mybot.idle()


main()
