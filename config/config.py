from datetime import timedelta
from telegram import KeyboardButton

TG_TOKEN = "324662497:AAFKDZUCNWtPa_1c_3MYwXB1vvHBiiUnoK8"

FORECAST_KEY = "cf20028a34237493da18f8cbadcc966d"

MAIN_DB_NAME = 'db/local.db'

# Forecast

temp_delta = 4
precipintens_delta = 0.3

subscr_time_delta = timedelta(minutes=30, seconds=0)

weather_emoji_dic = {
    'clear-day': '☀️',
    'clear-night': '🌓',
    'rain': '🌧️',
    'snow': '🌨️',
    'sleet': '🌨️',
    'wind': '🌬️️',
    'fog': '🌫️',
    'cloudy': '☁️',
    'partly-cloudy-day': '⛅',
    'partly-cloudy-night': '⛅'
}

# TBot

bot_menu_tree = {
    'menu_0': [['🌤 Погода', '⚙️ Настройки']],
    'menu_0_0': [['Умный прогноз', 'Текущая'], ['Ближайшая смена погоды', '🔙']],
    'menu_0_1': [[KeyboardButton('Обновить местоположение', request_location=True)], ['Подписка', '🔙']]
}
