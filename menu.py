#!/usr/bin/env python
# -*- coding: utf-8 -*-

import config
import tbot
from collections import OrderedDict
from sqliter import SQLiter
from telegram import KeyboardButton, ReplyKeyboardMarkup


menu_tree = {
    'main': ('into_menu', '1'), # (function_name, order_in_menu)
    'main.weather': ('into_menu', '1.1'),
    'main.weather.smart': ('smart_weather', '1.1.2'),
    'main.weather.current': ('current_weather', '1.1.3'),
    'main.weather.nearest': ('nearest_smart_weather', '1.1.4'),
    'main.weather.back': ('back_menu', '1.1.5'),
    'main.preferences': ('into_menu', '1.2'),
    'main.preferences.location': ('get_location', '1.2.1'),
    'main.preferences.language': ('set_language', '1.2.2'),
    'main.preferences.subscribe': ('subscribe', '1.2.3'),
    'main.preferences.back': ('back_menu', '1.2.4')
}
menu_tree_od = OrderedDict(sorted(menu_tree.items(), key=lambda t: t[1][1]))

menu_tree_text = {
    '🌤 Погода': 'weather',
    'Умный прогноз': 'smart',
    'Текущая': 'current',
    'Ближайшее изменение': 'nearest',
    '⚙️ Настройки': 'preferences',
    'Обновить местоположение': 'location',
    'Язык': 'language',
    'Подписка': 'subscribe',
    '🔙 Назад': 'back',
    '/start': 'main'
}


def handle_user_command(bot, update, user_command):
    
    # wrong command
    if user_command not in menu_tree_text:
        return
    tg_id = update.message.from_user.id
    new_part_menu = menu_tree_text[user_command]
        
    c = SQLiter()
    previous_user_menu = c.get_user_menu(tg_id)
    if new_part_menu == 'main':
        next_user_menu = new_part_menu
    else:
        next_user_menu = previous_user_menu + '.' + new_part_menu

    # wrong command
    if not next_user_menu in menu_tree:
        c.close()
        return

    try:
        result = getattr(tbot, menu_tree[next_user_menu][0])(bot, update, menu_path=next_user_menu)
    except (TypeError, NameError):
        pass

    if result is not None and 'menu_path' in result:
        c.set_user_menu(tg_id, result['menu_path'])

    c.close()


def get_reply_keyboard(menu_path):
    new_menu = []
    for key, value in menu_tree_od.items():
        if key.startswith(menu_path + '.') and \
                        key.count('.') == menu_path.count('.')+1:
            new_menu = add_button_to_menu(new_menu, key.split('.')[-1])

    return ReplyKeyboardMarkup(new_menu)


def get_reply_message(menu_path, tg_id):
    message = ''
    if menu_path == 'main.preferences':
        c = SQLiter()
        message = 'Текущие настройки:\n' \
                'Координаты для определения погоды - latitude: {lat}, longitude: {lng}\n' \
               'Подписка: {subscribed}, Время оповещения: {send_time}'.format(**c.user_preferences(tg_id))
        c.close()
    elif menu_path == 'main.weather':
        message = 'Меню погоды.\n' \
                  'Умный прогноз - кардинальные изменения погоды в ближайшие сутки\n' \
                  'Текущая - текущая погода\n' \
                  'Ближайшее изменение - когда ожидать кардинальное изменение погоды\n'
    elif menu_path == 'main':
        message = 'Главное меню.\n' \
                  'Погода - текущая погода и прогнозы\n' \
                  'Настройки - координаты, подписка и пр.'

    return message

def add_button_to_menu(menu, button_name):
    button_text = ''
    for key, value in menu_tree_text.items():
        if value == button_name:
            if button_name == 'location':
                button_text = KeyboardButton(key, request_location=True)
            else:
                button_text = key
            break

    if len(menu) == 0 or len(menu[-1]) == 2:
        menu.append([button_text])
    else:
        menu[-1].append(button_text)

    return menu

def get_preferences_text():
    return 'Preferences menu'