from datetime import datetime, date
from typing import Any
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.exception import arguments_exception


class datetime_convertor(abstract_convertor):
    """
    Конвертор для типов datetime и date.
    Преобразует дату/время в строковый формат ISO.
    """

    def convert(self, field: str, obj: Any) -> dict:
        """
        Преобразует объект datetime или date в ISO-строку.
        """

        # Валидация имени поля
        if not isinstance(field, str) or not field.strip():
            raise arguments_exception("Наименование поля должно быть непустой строкой", "field")

        # Валидация типа значения
        if not isinstance(obj, (datetime, date)):
            raise arguments_exception(
                f"Значение поля '{field}' должно быть datetime или date, получен '{type(obj).__name__}'", 
                "obj"
            )

        # Преобразование в ISO-строку
        formatted_value = obj.isoformat()
        return {field.strip(): formatted_value}