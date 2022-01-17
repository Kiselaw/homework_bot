from logging import StreamHandler


class TelegramHandler(StreamHandler):

    def __init__(self, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, bot):
        StreamHandler.__init__(self)
        self.TELEGRAM_TOKEN = TELEGRAM_TOKEN
        self.TELEGRAM_CHAT_ID = TELEGRAM_CHAT_ID
        self.bot = bot

    def emit(self, record):
        message = self.format(record)
        self.bot.send_message(self.TELEGRAM_CHAT_ID, message)
