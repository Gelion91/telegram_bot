import datetime
import logging
import os
import re
from glob import glob
from random import choice
import ephem
from telegram.ext import ConversationHandler
from telegram.ext import messagequeue as mq
import city
from utils import get_user_emo, get_keyboard, exit_keyboard, keyboard, YOUR_TURN, ANSWER, COUNT, is_cat
from bot import subscribers


def greet_user(update, context):
    user_data = context.user_data
    print(update.message.chat_id)
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


def planet_information(update, context):
    """Принимает команду от пользователя и выводит результат о местонахождении планеты"""

    your_question = update.message.text.split()
    quest = getattr(ephem, your_question[-1])
    constellation = ephem.constellation(quest(datetime.date.today()))
    update.message.reply_text(f'Сегодня {your_question[-1]} находится в созведии {constellation[-1]}')


def help_list(update, context):
    """Выводит список доступных команд к которым применима функция planet_information"""
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


def check_user_photo(update, context):
    update.message.reply_text('Обрабатываю фото')
    os.makedirs('downloads', exist_ok=True)
    photo_file = context.bot.getFile(update.message.photo[-1].file_id)
    filename = os.path.join('downloads', '{}.jpg'.format(photo_file.file_id))
    photo_file.download(filename)
    answer = is_cat(filename)
    update.message.reply_text(answer)


def subscribe(update, context):
    subscribers.add(update.message.chat_id)
    update.message.reply_text("Вы подписались, наберите /unsubscribe чтобы отписаться.")


def unsubscribe(update, context):
    if update.message.chat_id in subscribers:
        subscribers.remove(update.message.chat_id)
        update.message.reply_text("Вы отписались, наберите /subscribe чтобы подписаться.")
    else:
        update.message.reply_text('Вы не подписаны.')


@mq.queuedmessage
def send_updates(context):
    for chat_id in subscribers:
        context.bot.sendMessage(chat_id=chat_id, text="Привет!")
