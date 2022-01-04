class TokenError(Exception):
    def __str__(self):
        return f'Отсутствует обязательная переменная окружения'

class EmptyHomeworks(Exception):
    def __str__(self):
        return f'Нет новых домашек в ответе'

class StatusCodeError(Exception):
    def __str__(self):
        return f'Статус код ответа отличается от 200'

class Endpoint404(Exception):
    def __str__(self):
        return f'Эндпоинт не доступен. Код ответа 404'

class EmptyAPIResponse(Exception):
    def __str__(self):
        return f'Пустой ответ API'

class NotDocHomeworkStatus(Exception):
    def __str__(self):
        return f'Недокументированный статус домашней работы в ответе API'
