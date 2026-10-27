from typing import Any
from uuid import UUID
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.exception import arguments_exception


class basic_convertor(abstract_convertor):
    """
    Конвертор базовых типов данных: str, int, float, bool, None.
    Формирует словарь вида {field: value}.
    """

    def convert(self, field: str, obj: Any, visited: set | None = None) -> dict:
        """
        Преобразует базовое значение или UUID в пару ключ-значение словаря.
        """
        # Валидация имени поля
        if not isinstance(field, str) or (field != "" and not field.strip()):
            raise arguments_exception("Наименование поля должно быть непустой строкой", "field")

        # Проверка допустимости типа данных
        if obj is not None and not isinstance(obj, (str, int, float, bool, UUID)):
            raise arguments_exception(
                f"Тип '{type(obj).__name__}' не поддерживается basic_convertor", "obj"
            )

        # UUID преобразуем в строку для сериализации в JSON
        formatted_value = str(obj) if isinstance(obj, UUID) else obj
        return {field.strip(): formatted_value}