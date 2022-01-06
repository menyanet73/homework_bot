import logging
import os
import time
from http import HTTPStatus
from logging.handlers import RotatingFileHandler

import requests
from simplejson.errors import JSONDecodeError
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
    """Функция отправки сообщения в телеграм."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info(f'Сообщение удачно отправлено: {message}')
    except telegram.TelegramError as error:
        logger.error(f'Сбой при отправке сообщения: telegram_error: {error}')
    except Exception as error:
        logger.error(f'Сбой при отправке сообщения: {error}')


def get_api_answer(current_timestamp):
    """Обращение к API практикума, и передача json ответа."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if response.status_code == HTTPStatus.NOT_FOUND:
        raise exceptions.Endpoint404
    if response.status_code != HTTPStatus.OK:
        raise exceptions.StatusCodeError
    return response.json()


def check_response(response):
    """Функция изъятия домашек из ответа API."""
    if type(response) is not dict:
        logger.error('Некорректный тип. Ответ - не словарь.')
        raise TypeError('Некорректный тип. Ответ - не словарь.')
    homeworks = response.get('homeworks')
    if not homeworks:
        raise exceptions.EmptyHomeworks('Нет новых домашек в ответе')
    if type(homeworks) is not list:
        logger.error('Домашки в ответе, не в списке')
        raise TypeError('Домашки в ответе не в списке')
    return homeworks


def parse_status(homework):
    """Функция получения статуса домашней работы."""
    if 'homework_name' not in homework:
        raise KeyError('Отсутствует ключ homework_name в домашках')
    if 'status' not in homework:
        raise KeyError('Отсутствует ключ status в домашках')
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_status not in HOMEWORK_STATUSES:
        raise exceptions.NotDocHomeworkStatus(
            'Не документированный статус домашней работы'
        )
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Функция проверки наличия токенов в окружении."""
    if PRACTICUM_TOKEN is None:
        logger.error(
            'Не обнаружена обязательная переменная окружения:PRACTICUM_TOKEN'
        )
        return False
    elif TELEGRAM_CHAT_ID is None:
        logger.error(
            'Не обнаружена обязательная переменная окружения:TELEGRAM_CHAT_ID'
        )
        return False
    elif TELEGRAM_TOKEN is None:
        logger.error(
            'Не обнаружена обязательная переменная окружения:TELEGRAM_TOKEN'
        )
        return False
    else:
        return True


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    if check_tokens():
        while True:
            try:
                response = get_api_answer(current_timestamp)
                homeworks = check_response(response)
                for homework in homeworks:
                    message = parse_status(homework)
                    send_message(bot, message)
                    logger.info('Сообщение успешно отправлено')
                current_timestamp = response.get('current_date')
                time.sleep(RETRY_TIME)
            except requests.exceptions.RequestException as error:
                message = f'Ошибка запроса к серверу: {error}'
                logger.error(message)
                send_message(bot, message)
                time.sleep(RETRY_TIME)
            except exceptions.EmptyHomeworks as error:
                logger.debug(error)
                time.sleep(RETRY_TIME)
            except KeyError:
                message = 'Сбой в работе программы: Отсутствуют ожидаемые'
                +'ключи в ответе API'
                logger.error(message)
                send_message(bot, message)
                time.sleep(RETRY_TIME)
            except JSONDecodeError as error:
                message = f'Сбой в работе программы: {error}'
                logger.error(message)
                send_message(bot, message)
                time.sleep(RETRY_TIME)
            except Exception as error:
                message = f'Сбой в работе программы: {error}'
                logger.error(message)
                send_message(bot, message)
                time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
