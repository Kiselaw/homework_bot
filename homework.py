import logging
import os
import sys
import time
from http import HTTPStatus
from json import JSONDecodeError
from logging.handlers import RotatingFileHandler

import requests
import telegram
from dotenv import load_dotenv
from requests.exceptions import RequestException

from custom_exceptions import (EmptyError, FailedJSONError, FailedRequestError,
                               MessageSendingError, NoKeyError, Not200Error,
                               WrongDataTypeError)
from telegram_handler import TelegramHandler

load_dotenv()

SECONDS_IN_DAY = 86400
DAYS = 2

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
file_handler = RotatingFileHandler(
    'YPHWbot_logs.log', maxBytes=50_000_000, backupCount=5
)
logger.addHandler(file_handler)
handler.setFormatter(formatter)


def send_message(bot, message):
    """Отправка сообщения от бота."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info(f'Сообщение "{message}" успешно отправлено.')
    except telegram.error.TelegramError as error:
        raise MessageSendingError('Ошибка при отправке сообщения') from error


def get_api_answer(current_timestamp):
    """Получение ответа от API."""
    timestamp = current_timestamp
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except RequestException as error:
        raise FailedRequestError('Запрос не удался') from error
    if response.status_code != HTTPStatus.OK:
        raise Not200Error(
            f'Код ответа при запросе к API {response.status_code}'
        )
    try:
        return response.json()
    except JSONDecodeError as error:
        raise FailedJSONError('Проблема при преобразовании из JSON') from error


def check_response(response):
    """Проверка корректности ответа от API."""
    if not response:
        raise EmptyError('Ответ API пуст')
    if not isinstance(response, dict):
        raise TypeError('В ответе API не направлен словарь')
    try:
        homeworks = response['homeworks']
    except KeyError as error:
        raise NoKeyError('Отсутствует ключ "homeworks"') from error
    if not isinstance(homeworks, list):
        raise WrongDataTypeError(
            'Перечень домашек не пришел в виде списка'
        )
    if homeworks:
        return homeworks[0]
    else:
        logger.debug('Новых статусов нет')
        return False


def parse_status(homeworks):
    """Получение статуса домашней работы."""
    if 'homework_name' in homeworks:
        homework_name = homeworks['homework_name']
    else:
        raise KeyError('Отсутcтвует ключ "homework_name"')
    try:
        homework_status = homeworks['status']
        verdict = HOMEWORK_STATUSES[homework_status]
    except KeyError as error:
        logger.error(f'Отсутвует ключ: {error}', exc_info=True)
        raise NoKeyError(f'Отсутвует ключ: {error}') from error
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка наличия всех необходимых токенов."""
    token_list = {
        "PRACTICUM_TOKEN": PRACTICUM_TOKEN,
        "TELEGRAM_TOKEN": TELEGRAM_TOKEN,
        "TELEGRAM_CHAT_ID": TELEGRAM_CHAT_ID
    }
    for name, token in token_list.items():
        if token is None:
            logging.critical(
                f'Переменная окружения {name} отсутствует'
            )
            return False
    return True


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        sys.exit(1)
    error = []
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    telegram_handler = TelegramHandler(
        TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, bot, error
    )
    logger.addHandler(telegram_handler)
    handler.setFormatter(formatter)
    current_timestamp = int(time.time() - DAYS * SECONDS_IN_DAY)
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            homework_status = parse_status(homeworks)
            current_timestamp = response.get('current_date', current_timestamp)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message, exc_info=True)
        else:
            send_message(bot, homework_status)
        time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
