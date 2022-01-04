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
    """Обращение к API практикума, и передача json ответа"""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if response.status_code != 200:
        raise exceptions.StatusCodeError
    return response.json()
        #исключения: недоступность эндпоинта, другие сбои - еррор


def check_response(response):
    """Функция изъятия домашек из ответа API"""
    if type(response) is not dict:
        logger.error('Некорректный тип. Ответ - не словарь.')
        raise TypeError()
    homeworks = response.get('homeworks')
    if not homeworks:
        logger.error('Нет домашек в ответе')
        raise exceptions.EmptyHomeworks()
    if type(homeworks) is not list:
        logger.error('Домашки в ответе, не в списке')
        raise TypeError()
    return homeworks



def parse_status(homework):
    """Функция получения статуса домашней работы."""
    homework_name = homework['homework_name']
    homework_status = homework['status']
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Функция проверки наличия токенов в окружении."""
    if PRACTICUM_TOKEN == None:
        logger.error('Не обнаружена обязательная переменная окружения:' 
        'PRACTICUM_TOKEN')
        return False
    elif TELEGRAM_CHAT_ID == None:
        logger.error('Не обнаружена обязательная переменная окружения:' 
        'TELEGRAM_CHAT_ID')
        return False
    elif TELEGRAM_TOKEN == None:
        logger.error('Не обнаружена обязательная переменная окружения:' 
        'TELEGRAM_TOKEN')
        return False
    else:
        return True


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    if check_tokens() is True:
        while True:
            try:
                response = get_api_answer(current_timestamp)
                logger.error('Ошибка ответа от API')
                homeworks = check_response(response)
                for homework in homeworks:
                    message = parse_status(homework)
                    send_message(bot, message)
                    logger.info('Сообщение успешно отправлено')
                current_timestamp = response.get('current_date')
                time.sleep(RETRY_TIME)
            except Exception as error:
                message = f'Сбой в работе программы: {error}'
                logger.error(message)
                try:
                    send_message(bot, message)
                    logger.info('Сообщение успешно отправлено')
                except:    
                    logger.error('Не удается отправить сообщение в телеграм')
                time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
