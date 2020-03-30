from random import choice
from emoji import emojize
from telegram import KeyboardButton, ReplyKeyboardMarkup
from clarifai.rest import ClarifaiApp
import settings

YOUR_TURN, ANSWER, COUNT = range(3)

reply_keyboard = [
    ['Поиграть в города', 'Когда полнолуние', 'Количество слов'], ['Все команды', 'Прислать котика', 'Сменить аватар']
]
keyboard = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=False)
exit_keyboard = ReplyKeyboardMarkup([['выход']], resize_keyboard=True, one_time_keyboard=True)


def get_user_emo(user_data):
    if 'emo' in user_data:
        return user_data['emo']
    else:
        user_data['emo'] = emojize(choice(settings.USER_EMOJI), use_aliases=True)
        return user_data['emo']


def get_keyboard():
    contact_button = KeyboardButton('Прислать контакты', request_contact=True)
    location_button = KeyboardButton('Прислать координаты', request_location=True)
    start_keyboard = ReplyKeyboardMarkup([
        ['Покажи мне все!'], [contact_button, location_button]
    ], resize_keyboard=True, one_time_keyboard=True)
    return start_keyboard


def is_cat(file_name):
    app = ClarifaiApp(api_key=settings.CLARIFAI_API_KEY)
    model = app.public_models.general_model
    response = model.predict_by_filename(file_name, max_concepts=5)
    if response['status']['code'] == 10000:
        return ", ".join([concept['name'] for concept in response['outputs'][0]['data']['concepts']])


if __name__ == '__main__':
    is_cat('images/cat3.jpg')
