from datetime import datetime, date
from typing import Any
from uuid import UUID
from Src.Core.abstract_class import abstract_reference
from Src.Core.exception import arguments_exception
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.abstract_factory import abstract_factory
from Src.Logics.basic_convertor import basic_convertor
from Src.Logics.datetime_convertor import datetime_convertor
from Src.Logics.reference_convertor import reference_convertor


class convert_factory(abstract_factory):
    """
    Фабрика конверторов.
    Подбирает подходящий конвертор на основе внутреннего словаря сопоставления типов.
    """

    def __init__(self) -> None:
        """
        Инициализатор фабрики конверторов.
        Формирует реестр сопоставления типов и специализированных конверторов.
        """
        self._basic = basic_convertor()
        self._datetime = datetime_convertor()
        self._reference = reference_convertor(factory=self)

        # Реестр сопоставления типов 
        self.__mapping: dict[type, abstract_convertor] = {
            type(None): self._basic,
            str: self._basic,
            int: self._basic,
            float: self._basic,
            bool: self._basic,
            UUID: self._basic,
            datetime: self._datetime,
            date: self._datetime,
            abstract_reference: self._reference,
        }

    @property
    def mapping(self) -> dict[type, abstract_convertor]:
        """Словарь сопоставления типов и конверторов."""
        return self.__mapping

    def create(self, obj: Any) -> abstract_convertor:
        """Выбрать нужный конвертор для объекта."""
        if obj is None:
            return self.__mapping[type(None)]

        target_type = type(obj) if not isinstance(obj, type) else obj

        # Прямой поиск в словаре
        if target_type in self.__mapping:
            return self.__mapping[target_type]

        for cls in target_type.__mro__:
            if cls in self.__mapping:
                return self.__mapping[cls]

        raise arguments_exception(f"Для типа '{target_type.__name__}' конвертор не найден!", "obj")


    def convert(self, obj: Any, visited: set | None = None) -> Any:
        """
        Принимает любой объект и формирует структуру словарей.
        """
        if obj is None:
            return None

        # Если на вход подан список — обходим каждый элемент через фабрику
        if isinstance(obj, list):
            return [self.convert(item, visited=visited) for item in obj]

        # Если передан обычный словарь — рекурсивно обрабатываем значения
        if isinstance(obj, dict):
            return {k: self.convert(v, visited=visited) for k, v in obj.items()}

        convertor = self.create(obj)
        result = convertor.convert("", obj, visited=visited)
        return result.get("", result)