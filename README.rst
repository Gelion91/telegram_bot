CityBot
========

CityBot - это бот для Telegram с которым вы можете поиграть в "города" и многое другое.

Установка
=========

Создайте виртуальное окружение и активируйте его. В виртуальном окружении выполните:

.. code-block:: text

    pip install -r requirements.txt

Положите картинки с котиками в папку images. Название файлов должно начинаться с cat, а заканчиваться .jpg например cat123.jpg

Настройка
---------

Создайте файл settings.py добавьте туда следующие настройки

.. code-block:: python

    PROXY = {'proxy_url': 'socks5://ВАШ ПРОКСИ', 'urllib3_proxy_kwargs': {'username': 'ЛОГИН', 'password': 'ПАРОЛЬ'}}

    API_KEY = 'API ключ который вы получили от BotFather'

    USER_EMOJI = [':smiley_cat:', ':smiling_imp:', ':panda_face:', ':dog:']

Запуск
-------

В активированном виртуальном окружении выполните

.. code-block::

    python bot.py
