import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)

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


def send_message(bot, message):
    """Отправка сообщения от бота"""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info(f'Сообщение "{message}" успешно отправлено.')
    except Exception as error:
        logger.error(f'Ошибка при отправке сообщения: {error}', exc_info=True)


def get_api_answer(current_timestamp):
    """Получение ответа от API"""
    timestamp = current_timestamp
    params = {'from_date': timestamp}
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if response.status_code != HTTPStatus.OK:
        logger.error('Эндпоинт недоступен')
        raise ConnectionError
    try:
        isinstance(response.json(), dict)
    except ValueError as error:
        logger.error(
            f'Несоответствующий тип возвращаемых данных: {error}',
            exc_info=True)
        raise
    else:
        return response.json()


def check_response(response):
    """Проверка корректности ответа от API"""
    if response:
        try:
            homework = response['homeworks']
        except KeyError:
            logger.error('Отсутсвует ключ "homeworks"', exc_info=True)
            raise
        else:
            if isinstance(homework, list):
                pass
            else:
                logger.error('Перечень домашек не пришел в виде списка')
                raise ValueError
    else:
        logger.error('Ответ API пуст')
        raise Exception
    if homework:
        return homework[0]
    else:
        return False


def parse_status(homework):
    """Получение статуса домашней работы"""
    if homework is False:
        return False
    if 'homework_name' in homework:
        homework_name = homework['homework_name']
    else:
        logger.error('Отсутcтвует ключ "homework_name"')
        raise KeyError
    try:
        homework_status = homework['status']
        verdict = HOMEWORK_STATUSES[homework_status]
    except KeyError as error:
        logger.error(f'Отсутвует ключ: {error}', exc_info=True)
        raise
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка наличия всех необходимых токенов"""
    token_list = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_TOKEN]
    for token in token_list:
        if token is None:
            logging.critical(f'Переменная окружения {token} отсутствует')
            return False
    return True


def main():
    """Основная логика работы бота."""
    check_tokens()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time() - 30 * 86400)
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            homework_status = parse_status(homework)
            current_timestamp = response['current_date']
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            time.sleep(RETRY_TIME)
        else:
            if homework_status is False:
                time.sleep(RETRY_TIME)
            else:
                send_message(bot, homework_status)
                time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
