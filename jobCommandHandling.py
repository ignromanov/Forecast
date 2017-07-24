#!/usr/bin/env python
# -*- coding: utf-8 -*-

from weatherForecast import WeatherForecast


class JobCommandHandling(object):

    def __init__(self, bot, tg_id, **user_location):
        self.bot = bot
        self.user_id = tg_id
        self.weatherForecast = WeatherForecast(**user_location)

    def current_weather(self):
        self.bot.sendMessage(
            self.user_id, self.weatherForecast.get_current_weather())

    def smart_weather(self):
        self.bot.sendMessage(
            self.user_id, self.weatherForecast.today_smart_weather())

    def nearest_smart_weather(self):
        self.bot.sendMessage(
            self.user_id, self.weatherForecast.nearest_weather_change())
