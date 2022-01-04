class TokenError(Exception):
    def __str__(self):
        return f'Отсутствует обязательная переменная окружения'

class EmptyHomeworks(Exception):
    def __str__(self):
        return f'Отсутствуют домашние задания в ответе API'

class StatusCodeError(Exception):
    def __str__(self):
        return f'Статус код ответа отличается от 200'

class EmptyAPIResponse(Exception):
    def __str__(self):
        return f'Пустой ответ API'
