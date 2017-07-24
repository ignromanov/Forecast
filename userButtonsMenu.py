from telegram import ReplyKeyboardMarkup, KeyboardButton
from collections import OrderedDict
from SQLiter import SQLiter




__MENU_TREE__ = {
    'main': ('_into_menu', '1', 'menu'),  # (function_name, order_in_menu, (menu, function))
    'main.weather': ('_into_menu', '1.1', 'menu'),
    'main.weather.smart': ('_smart_weather', '1.1.2', 'function'),
    'main.weather.current': ('_current_weather', '1.1.3', 'function'),
    'main.weather.nearest': ('_nearest_smart_weather', '1.1.4', 'function'),
    'main.weather.back': ('_into_menu', '1.1.5', 'menu'),
    'main.preferences': ('_into_menu', '1.2', 'menu'),
    'main.preferences.location': ('_get_location', '1.2.1', 'function'),
    'main.preferences.language': ('_set_language', '1.2.2', 'function'),
    'main.preferences.subscribe': ('_subscribe', '1.2.3', 'function'),
    'main.preferences.back': ('_into_menu', '1.2.4', 'menu')
}
__MENU_TREE_OD__ = OrderedDict(sorted(__MENU_TREE__.items(), key=lambda t: t[1][1]))
__MENU_TREE_TEXT__ = {
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


class UserButtonsMenu(object):
    def __init__(self, user_id, user_command):

        self.new_menu_correct = True
        self.user_command = user_command
        self.user_id = user_id

        self.__c = SQLiter()
        self.__prev_user_menu_id = self.__c.get_user_menu(self.user_id)

        new_part_menu = __MENU_TREE_TEXT__[self.user_command]
        if new_part_menu == 'main':
            self.__next_user_menu_id = new_part_menu
        elif new_part_menu == 'back':
            self.__next_user_menu_id = '.'.join(self.__prev_user_menu_id.split('.')[:-1])
        else:
            self.__next_user_menu_id = self.__prev_user_menu_id + '.' + new_part_menu

        # wrong command
        if self.__next_user_menu_id not in __MENU_TREE__:
            self.new_menu_correct = False
            return

        self.user_menu_handler = __MENU_TREE__[self.__next_user_menu_id][0]
        self.user_command_type = __MENU_TREE__[self.__next_user_menu_id][2]

        self._init_reply_menu()
        self._init_reply_message()

    def __del__(self):
        if self.user_command_type == 'menu':
            self.__c.set_user_menu(self.user_id, self.__next_user_menu_id)

    def _init_reply_menu(self):
        self.__new_menu = []
        for key, value in __MENU_TREE_OD__.items():
            if key.startswith(self.__next_user_menu_id + '.') and \
                            key.count('.') == self.__next_user_menu_id.count('.') + 1:
                self._add_button_to_menu(key.split('.')[-1])

        self.reply_menu = ReplyKeyboardMarkup(self.__new_menu)

    def _init_reply_message(self):
        self.reply_message = ''
        if self.__next_user_menu_id == 'main.preferences':
            self.reply_message = ('Текущие настройки:\n'
                        'Координаты для определения погоды - latitude: {lat}, longitude: {lng}\n'
                        'Подписка: {subscribed}, Время оповещения: {send_time}') \
                .format(**self.__c.user_preferences(self.user_id))
        elif self.__next_user_menu_id == 'main.weather':
            self.reply_message = ('Меню погоды.\n'
                        'Умный прогноз - кардинальные изменения погоды в ближайшие сутки\n'
                        'Текущая - текущая погода\n'
                        'Ближайшее изменение - когда ожидать кардинальное изменение погоды\n')
        elif self.__next_user_menu_id == 'main':
            self.reply_message = ('Главное меню.\n'
                        'Погода - текущая погода и прогнозы\n'
                        'Настройки - координаты, подписка и пр.')
        elif self.__next_user_menu_id == 'main.preferences.language':
            self.reply_message = ('Воспользуйтесь одной из команд для смены языка:\n'
                        '/language_ru - русский язык\n'
                        '/language_en - english')

    def _add_button_to_menu(self, button_name):
        button_text = ''
        for key, value in __MENU_TREE_TEXT__.items():
            if value == button_name:
                if button_name == 'location':
                    button_text = KeyboardButton(key, request_location=True)
                else:
                    button_text = key
                break

        if len(self.__new_menu) == 0 or len(self.__new_menu[-1]) == 2:
            self.__new_menu.append([button_text])
        else:
            self.__new_menu[-1].append(button_text)