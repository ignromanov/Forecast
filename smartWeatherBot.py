#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.

import logging
from datetime import datetime

import pytz
from telegram import ChatAction
from telegram.ext import Updater, MessageHandler, Filters, Job

import weatherForecast
from SQLiter import SQLiter
from config import __config__
from userCommandHandling import UserCommandHandling
from jobCommandHandling import JobCommandHandling


class SmartWeatherBot(object):
    def __init__(self):
        # Enable logging
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)

        self.logger = logging.getLogger(__name__)
        self.__c__ = SQLiter()

        self.subscribe_job = Job(self._subscription_job_callback, __config__.subscr_time_delta.total_seconds())

        # Create the EventHandler and pass it your bot's token.
        self.updater = Updater(__config__.TG_TOKEN)
        self.updater.job_queue.put(self.subscribe_job)

        # Get the dispatcher to register handlers
        self.dp = self.updater.dispatcher

        # on different commands - answer in Telegram
        # self.dp.add_handler(CommandHandler("start", self.start))
        # self.dp.add_handler(CommandHandler("help", self.help, pass_args=True))
        # self.dp.add_handler(CommandHandler("language_ru", self.subscribe))
        self.dp.add_handler(MessageHandler(Filters.text, self._handle_text_message))
        # self.dp.add_handler(MessageHandler(Filters.location, self.location))

        # log all errors
        self.dp.add_error_handler(self.error)

        # Start the Bot
        self.updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        self.updater.idle()

    @staticmethod
    def _handle_text_message(bot, update):
        bot.sendChatAction(update.message.chat_id, ChatAction.TYPING)
        UserCommandHandling(bot, update)

    @staticmethod
    def _subscription_job_callback(bot, job):
        users_data = SQLiter().current_subscriptions(datetime.now(__config__.SERVER_TZ).astimezone(pytz.utc))
        if len(users_data) == 0:
            return
        for user_data in users_data:
            JobCommandHandling(bot, **user_data).smart_weather()

    def error(self, update, error):
        self.logger.warn('Update "%s" caused error "%s"' % (update, error))
