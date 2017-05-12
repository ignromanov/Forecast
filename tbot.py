#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.

import logging
from datetime import datetime
from telegram import KeyboardButton, ReplyKeyboardMarkup, ChatAction
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Job

import forecast
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
    update.message.reply_text('Hi, {} {}!'.format(user_dic['first_name'], user_dic['last_name']),
                              reply_markup=reply_keyboard_markup(update.message.from_user.id, 'menu_0'))


def reply_keyboard_markup(tg_id, new_menu):
    # c = SQLiter()
    # user_menu = c.get_user_menu(tg_id)
    # c.close()

    new_rkm = ReplyKeyboardMarkup(config.bot_menu_tree[new_menu])

    # c.set_user_menu(tg_id, new_menu)
    return new_rkm


def subscribe(bot, update):
    c = SQLiter()
    c.subscribe(update.message.from_user.id)
    c.close()


def preferences(bot, update):
    location_keyboard = KeyboardButton('Местоположение')
    subscribe_keyboard = KeyboardButton('Подписка')
    update.message.reply_text('Send your location',
                              reply_markup=ReplyKeyboardMarkup([[location_keyboard, subscribe_keyboard]]))


def help(bot, update):
    update.message.reply_text('Help!')


def echo(bot, update):
    update.message.reply_text(update.message.text)


def handle_text_message(bot, update):
    bot.sendChatAction(update.message.chat_id, ChatAction.TYPING)

    c = SQLiter()
    user_location = c.get_user_location(update.message.from_user.id)
    c.close()

    um, bm = update.message, config.bot_menu_tree
    if um.text == bm['menu_0_0'][0][1]:  # 'Текущая'
        um.reply_text(forecast.current_weather(**user_location))
    elif um.text == bm['menu_0_0'][0][0]:  # 'Smart weather'
        um.reply_text(forecast.today_smart_weather(**user_location))
    elif um.text == bm['menu_0_0'][1][0]:  # 'Ближайшая смена погоды'
        um.reply_text(forecast.nearest_weather_change(**user_location))
    elif um.text == bm['menu_0'][0][0]:  # Погода
        um.reply_text('Какая погода вам интересна?',
                      reply_markup=reply_keyboard_markup(um.from_user.id, 'menu_0_0'))
    elif um.text == bm['menu_0'][0][1]:  # Настройки
        um.reply_text('Настройки бота',
                      reply_markup=reply_keyboard_markup(um.from_user.id, 'menu_0_1'))
    elif um.text == bm['menu_0_0'][1][1] or um.text == bm['menu_0_1'][1][1]:  # Назад
        um.reply_text('Главное меню',
                      reply_markup=reply_keyboard_markup(um.from_user.id, 'menu_0'))



def subscription_job_callback(bot, job):
    c = SQLiter()
    list_of_users = c.current_subscriptions(datetime.now())
    c.close()
    if len(list_of_users) == 0:
        return

    for user_dic in list_of_users:
        bot.sendMessage(user_dic['tg_id'], forecast.today_smart_weather(**user_dic))


def location(bot, update):
    c = SQLiter()
    with update.message as m:
        c.save_location(m.from_user.id, m.location.latitude, m.location.longitude)
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
    dp.add_handler(CommandHandler("subscribe", subscribe))
    dp.add_handler(CommandHandler("preferences", preferences))

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
