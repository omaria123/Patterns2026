from enum import StrEnum


class filter_type_enum(StrEnum):
    """Перечисление доступных вариантов сравнения при фильтрации."""
    EQUALS = "equals"
    LIKE = "like"