class EmptyHomeworks(Exception):
    """Исключение, на случай, если нет изменений в проверках домашек."""

    def __str__(self):
        return 'Нет новых домашек в ответе'


class StatusCodeError(Exception):
    """Исключение, если статус код ответа отличается от 200."""

    def __str__(self):
        return 'Статус код ответа отличается от 200'


class Endpoint404(Exception):
    """Исключение, если не доступен эндпоинт API."""

    def __str__(self):
        return 'Эндпоинт не доступен. Код ответа 404'


class EmptyAPIResponse(Exception):
    """Исключение, если API возвращает пустой ответ."""

    def __str__(self):
        return 'Пустой ответ API'


class NotDocHomeworkStatus(Exception):
    """Исключение, если в ответе возвращен неизвестный статус домашки."""

    def __str__(self):
        return 'Недокументированный статус домашней работы в ответе API'
