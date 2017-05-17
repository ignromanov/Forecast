#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.

import logging
from datetime import datetime
from telegram import KeyboardButton, ReplyKeyboardMarkup, ChatAction
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Job
from menu import handle_user_command, get_reply_keyboard, get_reply_message

import forecast
import pytz
from config import config
from sqliter import SQLiter

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    c = SQLiter()
    user_dic = c.find_user(update.message.from_user)
    c.close()
    # update.message.reply_text('Hi, {} {}!'.format(user_dic['first_name'], user_dic['last_name']),
    #                           reply_markup=reply_keyboard_markup(update.message.from_user.id, 'menu_0'))
    handle_user_command(bot, update, update.message.text)

def help(bot, update):
    update.message.reply_text('Help!')


def echo(bot, update):
    update.message.reply_text(update.message.text)


def handle_text_message(bot, update):
    bot.sendChatAction(update.message.chat_id, ChatAction.TYPING)
    handle_user_command(bot, update, update.message.text)

def into_menu(bot, update, menu_path):
    update.message.reply_text(get_reply_message(menu_path, update.message.from_user.id), reply_markup=get_reply_keyboard(menu_path))
    return {'menu_path': menu_path}

def back_menu(bot, update, menu_path):
    menu_path = '.'.join(menu_path.split('.')[:-2])
    update.message.reply_text(get_reply_message(menu_path, update.message.from_user.id), reply_markup=get_reply_keyboard(menu_path))
    return {'menu_path': menu_path}

def smart_weather(bot, update, **kwargs):
    c = SQLiter()
    user_position = c.get_user_location(update.message.from_user.id)
    c.close()
    update.message.reply_text(forecast.today_smart_weather(**user_position))

def current_weather(bot, update, **kwargs):
    c = SQLiter()
    user_position = c.get_user_location(update.message.from_user.id)
    c.close()
    update.message.reply_text(forecast.current_weather(**user_position))

def nearest_smart_weather(bot, update, **kwargs):
    c = SQLiter()
    user_position = c.get_user_location(update.message.from_user.id)
    c.close()
    update.message.reply_text(forecast.nearest_weather_change(**user_position))

def get_location(bot, update, **kwargs):
    pass

def set_language(bot, update, **kwargs):
    update.message.reply_text(
            'Воспользуйтесь одной из команд для смены языка:\n'
            '/language_ru - русский язык\n'
            '/language_en - english')

def subscribe(bot, update, **kwargs):
    c = SQLiter()
    c.subscribe(update.message.from_user.id)
    c.close()
    update.message.reply_text('Подписка обновлена')

def subscription_job_callback(bot, job):
    c = SQLiter()
    list_of_users = c.current_subscriptions(datetime.now(config.SERVER_TZ).astimezone(pytz.utc))
    c.close()
    if len(list_of_users) == 0:
        return

    for user_dic in list_of_users:
        bot.sendMessage(user_dic['tg_id'], forecast.today_smart_weather(**user_dic))


def location(bot, update):
    c = SQLiter()
    m = update.message
    c.save_location(m.from_user.id, m.location.latitude, m.location.longitude,
                    forecast.get_timezone_by_coords(m.location.latitude, m.location.longitude))
    c.close()
    update.message.reply_text("Your location saved")


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    subscription_job = Job(subscription_job_callback, config.subscr_time_delta.total_seconds())

    # Create the EventHandler and pass it your bot's token.
    updater = Updater(config.TG_TOKEN)
    updater.job_queue.put(subscription_job)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("language_ru", subscribe))
    # dp.add_handler(CommandHandler("preferences", preferences))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, handle_text_message))

    dp.add_handler(MessageHandler(Filters.location, location))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
