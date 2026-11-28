from enum import StrEnum


class log_type_enum(StrEnum):
    """Перечисление уровней сообщений логирования."""

    ERROR = "ERROR"
    INFO = "INFO"
    DEBUG = "DEBUG"