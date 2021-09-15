#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
"""

import logging
import scraper
from datetime import datetime, timedelta
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import time
import os

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

os.environ['TZ'] = 'Europe/Amsterdam'
time.tzset()

logger = logging.getLogger(__name__)

schedule = scraper.get_schedule()


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

def now(update: Update, context: CallbackContext) -> None:
    les = scraper.get_lesson(schedule, datetime.now().strftime("%H:%M"))
    update.message.reply_text(f"{les['les']}, {les['lokaal']}")

def next(update: Update, context: CallbackContext) -> None:
    last_hour_date_time = datetime.now() + timedelta(hours = 1)
    time_now = last_hour_date_time.strftime("%H:%M")
    les = scraper.get_lesson(schedule, time_now)
    update.message.reply_text(f"{time_now}: {les['les']}, {les['lokaal']}")

def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("1997658287:AAGeV3LDM96EqfcsHryPE3-wK53B2WMKR9M")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("now", now))
    dispatcher.add_handler(CommandHandler("next", next))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
