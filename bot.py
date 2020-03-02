
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import settings
from my_handlers import planet_information, counter, full_moon, start, cities, help_list, send_cat, change, received_information, \
    numbers, greet_user, get_contact, get_location
from utils import YOUR_TURN, ANSWER, COUNT

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log')


def main():
    """Тело бота"""
    mybot = Updater(settings.API_KEY, request_kwargs=settings.PROXY, use_context=True)
    logging.info('Бот запускается')
    dp = mybot.dispatcher
    dp.add_handler(CommandHandler('planet', planet_information, pass_user_data=True))
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


if __name__ == "__main__":
    main()
