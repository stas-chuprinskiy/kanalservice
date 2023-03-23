class CustomError(Exception):
    """Базовый класс кастомных исключений."""

    pass


class GetSheetDataError(CustomError):
    """Ошибка получения данных таблицы."""

    pass
