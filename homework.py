import logging
import os
import time
from logging.handlers import RotatingFileHandler

import requests
import telegram
from dotenv import load_dotenv

import exceptions

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler(
    'homework_logger.log',
    maxBytes=5000000,
    backupCount=3
)
handler.setFormatter(logging.Formatter(
    '%(asctime)s [%(levelname)s] %(message)s'
))
logger.addHandler(handler)


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
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info(f'Сообщение удачно отправлено: {message}')
    except Exception:
        logger.error(f'Сбой при отправке сообщения')

def get_api_answer(current_timestamp):
    timestamp = current_timestamp or int(time.time())
    timestamp = 0
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code != 200:
            logger.error('Статус код ответа отличается от 200')
            raise exceptions.StatusCodeError()
        return response.json()
    except Exception:
        logger.error('')
        #исключения: недоступность эндпоинта, другие сбои - еррор

def check_response(response):
    try:
        homeworks = response.get('homeworks')
        if not homeworks:
            logger.info('Отсутствуют домашние задания в ответе API')
            raise exceptions.EmptyHomeworks()
        return homeworks
    except Exception:
        logger.error('Отсутствует ключ "homeworks" в ответе API')


def parse_status(homework):
    try:
        homework_name = homework['homework_name']
        homework_status = homework['status']
        verdict = HOMEWORK_STATUSES[homework_status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    except Exception:
        logger.error('Не документированный статус домашней работы в ответе')
        # отсутствие в ответе новых статусов

def check_tokens():
    if PRACTICUM_TOKEN == None:
        logger.error('Отсутствует PRACTICUM_TOKEN')
        return False
    elif TELEGRAM_CHAT_ID == None:
        logger.error('Отсутствует TELEGRAM_CHAT_ID')
        return False
    elif TELEGRAM_TOKEN == None:
        logger.error('Отсутствует TELEGRAM_TOKEN')
        return False
    else:
        return True


def main():
    """Основная логика работы бота."""

    

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    ...

    if check_tokens() is True:
        while True:
            try:
                response = get_api_answer(current_timestamp)
                homeworks = check_response(response)
                if type(homeworks) != list:
                    for homework in homeworks:
                        message = parse_status(homework)
                        send_message(bot, message)


                ...

                current_timestamp = response.get('current_date')
                time.sleep(RETRY_TIME)

            except Exception as error:
                message = f'Сбой в работе программы: {error}'
                logger.error(message)
                send_message(bot, message)
                time.sleep(RETRY_TIME)
            else:
                logger.error('Не удается отправить сообщение в телеграм')


if __name__ == '__main__':
    main()
