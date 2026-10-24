from typing import Any
from Src.Core.abstract_class import abstract_reference
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.exception import arguments_exception


class reference_convertor(abstract_convertor):
    """
    Конвертор для доменных моделей, унаследованных от abstract_reference.
    Формирует вложенный словарь {field: {свойства_модели}}.
    """

    def __init__(self, factory=None) -> None:
        """
        Инициализатор конвертора ссылочных сущностей.
        """
        self._factory = factory

    @property
    def factory(self):
        """Геттер ссылки на фабрику конверторов."""
        return self._factory

    @factory.setter
    def factory(self, value):
        """Сеттер ссылки на фабрику конверторов."""
        self._factory = value

    def convert(self, field: str, obj: Any, visited: set | None = None) -> dict:
        """
        Преобразует доменную модель в словарь с рекурсивным обходом свойств.
        """

        # Валидация имени поля
        if not isinstance(field, str) or not field.strip():
            raise arguments_exception("Наименование поля должно быть непустой строкой", "field")

        # Валидация типа объекта
        if not isinstance(obj, abstract_reference):
            raise arguments_exception(
                f"Объект поля '{field}' должен наследовать abstract_reference", "obj"
            )

        # Защита от зацикливания 
        if visited is None:
            visited = set()

        if self._factory is not None:
            model_dict = self._factory.convert(obj, visited=visited)
        else:
            model_dict = {
                "id": str(obj.id),
                "name": str(obj.name)
            }

        return {field.strip(): model_dict}