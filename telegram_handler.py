from logging import StreamHandler


class TelegramHandler(StreamHandler):

    def __init__(self, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, bot):
        super().__init__(self)
        self.TELEGRAM_TOKEN = TELEGRAM_TOKEN
        self.TELEGRAM_CHAT_ID = TELEGRAM_CHAT_ID
        self.bot = bot

    def emit(self, record):
        error = []
        message = self.format(record)
        if message not in error:
            error.insert(0, message)
            self.bot.send_message(self.TELEGRAM_CHAT_ID, message)
