from logging import StreamHandler


class TelegramHandler(StreamHandler):

    def __init__(self, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, bot, error):
        super().__init__(self)
        self.TELEGRAM_TOKEN = TELEGRAM_TOKEN
        self.TELEGRAM_CHAT_ID = TELEGRAM_CHAT_ID
        self.bot = bot
        self.error = error

    def emit(self, record):
        message = self.format(record)
        if message != self.error:
            self.error = message
            self.bot.send_message(self.TELEGRAM_CHAT_ID, message)
