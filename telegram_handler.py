from logging import StreamHandler

import telegram


class TelegramHandler(StreamHandler):

    def __init__(self, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID):
        StreamHandler.__init__(self)
        self.TELEGRAM_TOKEN = TELEGRAM_TOKEN
        self.TELEGRAM_CHAT_ID = TELEGRAM_CHAT_ID
        self.bot = telegram.Bot(token=TELEGRAM_TOKEN)

    def emit(self, record):
        message = self.format(record)
        self.bot.send_message(self.TELEGRAM_CHAT_ID, message)
