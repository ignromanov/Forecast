#!/usr/bin/env python
# -*- coding: utf-8 -*-

from weatherForecast import WeatherForecast
from userButtonsMenu import UserButtonsMenu
from SQLiter import SQLiter


class UserCommandHandling(object):

    def __init__(self, bot, update):

        self.bot = bot
        self.message = update.message
        self.user_id = self.message.from_user.id
        self.chat_id = self.message.chat_id
        self.user_command = self.message.text

        self.__c = SQLiter()

        self.user_menu = UserButtonsMenu(self.user_id, self.user_command)
        if not self.user_menu.new_menu_correct:
            return

        # try:
        handler_func = self.__getattribute__(self.user_menu.user_menu_handler)
        # call user_menu_handler method
        handler_func()
        # except (TypeError, NameError):
        #     raise NameError

    # Main
    # Define a few command handlers. These usually take the two arguments bot and
    # update. Error handlers also receive the raised TelegramError object in error.
    def _start(self):
        self.__c.find_user(self.message.from_user)
        # update.message.reply_text('Hi, {} {}!'.format(user_dic['first_name'], user_dic['last_name']),
        #                           reply_markup=reply_keyboard_markup(update.message.from_user.id, 'menu_0'))

    def _help(self):
        self.message.reply_text('Help!')

    def _echo(self):
        self.message.reply_text(self.message.text)

    def _into_menu(self):
        self.message.reply_text(text=self.user_menu.reply_message, reply_markup=self.user_menu.reply_menu)

    # Weather
    def _init_weather_forecast(self):
        self.weatherForecast = WeatherForecast(**self._user_location())

    def _current_weather(self):
        self._init_weather_forecast()
        self.message.reply_text(
            self.weatherForecast.get_current_weather())

    def _smart_weather(self):
        self._init_weather_forecast()
        self.message.reply_text(
            self.weatherForecast.today_smart_weather())

    def _nearest_smart_weather(self):
        self._init_weather_forecast()
        self.message.reply_text(
            self.weatherForecast.nearest_weather_change())

    def _get_location(self):
        pass

    def _set_language(self):
        pass
        # self.message.reply_text(get_reply_message(kwargs['menu_path']))

    def _subscribe(self):
        self.__c.subscribe(self.user_id)
        self.message.reply_text('Подписка обновлена')

    def _location(self):
        with self.message.location as l:
            self.__c.save_location(self.user_id, l.latitude, l.longitude,
                                   self.weatherForecast.get_timezone_by_coords(l.latitude, l.longitude))
        self.message.reply_text("Your location saved")

    def _user_location(self):
        return self.__c.get_user_location(self.user_id)
