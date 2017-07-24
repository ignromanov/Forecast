#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import timedelta
from telegram import KeyboardButton
from pytz import timezone

TG_TOKEN = "324662497:AAFKDZUCNWtPa_1c_3MYwXB1vvHBiiUnoK8"

FORECAST_URL = 'https://api.darksky.net/forecast'
FORECAST_KEY = "cf20028a34237493da18f8cbadcc966d"

MAIN_DB_NAME = 'db/local.db'

SERVER_TZ = timezone('Europe/Moscow')

# Forecast

temp_delta = 4
precipintens_delta = 0.3

subscr_time_delta = timedelta(hours=3, minutes=0, seconds=0)
subsct_default_time = '08:00'

