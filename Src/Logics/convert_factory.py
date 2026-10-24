from datetime import datetime, date
from typing import Any
from uuid import UUID
from Src.Core.abstract_class import abstract_reference
from Src.Core.exception import arguments_exception
from Src.Logics.basic_convertor import basic_convertor
from Src.Logics.datetime_convertor import datetime_convertor
from Src.Logics.reference_convertor import reference_convertor


class convert_factory:
    """
    Фабрика конвертации произвольных объектов в структуры словарей (dict).
    Координирует работу специализированных конверторов (basic, datetime, reference)
    и управляет рекурсивным обходом вложенных моделей и списков.
    """

    def __init__(self) -> None:
        """
        Инициализатор фабрики конверторов.
        Создает экземпляры базовых конверторов и связывает их.
        """
        self._basic = basic_convertor()
        self._datetime = datetime_convertor()
        self._reference = reference_convertor(factory=self)

    @property
    def basic(self) -> basic_convertor:
        """Геттер конвертора базовых типов."""
        return self._basic

    @property
    def datetime(self) -> datetime_convertor:
        """Геттер конвертора даты и времени."""
        return self._datetime

    @property
    def reference(self) -> reference_convertor:
        """Геттер конвертора ссылочных типов."""
        return self._reference

    def _get_properties(self, obj: Any) -> list[str]:
        """
        Вспомогательный метод: извлекает имена всех публичных @property объекта.
        """
        props = []
        for cls in type(obj).__mro__:
            for name, attr in cls.__dict__.items():
                if isinstance(attr, property) and not name.startswith("_") and name not in props:
                    props.append(name)
        return props

    def convert(self, obj: Any, visited: set | None = None) -> Any:
        """
        Принимает любой объект и формирует структуру словарей.
        """
        if obj is None:
            return None

        # Если на вход подан список — обходим каждый элемент через фабрику
        if isinstance(obj, list):
            return [self.convert(item, visited=visited) for item in obj]

        # Если подан простой тип
        if isinstance(obj, (str, int, float, bool, UUID)):
            res = self._basic.convert("value", obj)
            return res["value"]

        # Если подана дата/время
        if isinstance(obj, (datetime, date)):
            res = self._datetime.convert("value", obj)
            return res["value"]

        # Если подана доменная сущность (abstract_reference)
        if isinstance(obj, abstract_reference):
            if visited is None:
                visited = set()

            obj_id = str(obj.id)
            if obj_id in visited:
                # Прерывание бесконечного цикла рекурсии
                return None

            current_visited = set(visited)
            current_visited.add(obj_id)

            result_dict = {}
            properties = self._get_properties(obj)

            for prop_name in properties:
                prop_value = getattr(obj, prop_name, None)

                # Диспетчеризация поля по его типу:
                if prop_value is None:
                    result_dict[prop_name] = None
                elif isinstance(prop_value, list):
                    result_dict[prop_name] = [self.convert(x, visited=current_visited) for x in prop_value]
                elif isinstance(prop_value, abstract_reference):
                    # Проверяем на прямое зацикливание 
                    if prop_value is obj or str(prop_value.id) in current_visited:
                        result_dict[prop_name] = None
                    else:
                        converted_ref = self._reference.convert(prop_name, prop_value, visited=current_visited)
                        result_dict[prop_name] = converted_ref[prop_name]
                elif isinstance(prop_value, (datetime, date)):
                    converted_dt = self._datetime.convert(prop_name, prop_value)
                    result_dict[prop_name] = converted_dt[prop_name]
                elif isinstance(prop_value, (str, int, float, bool, UUID)):
                    converted_basic = self._basic.convert(prop_name, prop_value)
                    result_dict[prop_name] = converted_basic[prop_name]
                else:
                    # Резервный вариант для прочих вложенных объектов
                    result_dict[prop_name] = self.convert(prop_value, visited=current_visited)

            return result_dict

        # Если передан обычный словарь — рекурсивно обрабатываем значения
        if isinstance(obj, dict):
            return {k: self.convert(v, visited=visited) for k, v in obj.items()}

        raise arguments_exception(f"Не удалось сериализовать объект типа '{type(obj).__name__}'", "obj")