class TokenError(Exception):
    def __str__(self):
        return f'Отсутствует обязательная переменная окружения'