from datetime import datetime
from typing import Any
from uuid import UUID

from Src.Core.abstract_class import abstract_reference
from Src.Core.abstract_prototype import abstract_prototype
from Src.Core.exception import arguments_exception
from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.filter_type_enum import filter_type_enum


class prototype(abstract_prototype):
    """
    Универсальная реализация шаблона Прототип.
    Фильтрует коллекции любых доменных моделей и возвращает новый экземпляр prototype.
    """
    _CONTROL_FIELDS = {"type", "filter_type", "nested", "start_period", "end_period"}
    def __init__(self, source: list) -> None:
        """Инициализирует прототип исходным списком моделей."""
        super().__init__(source)

    def clone(self, filter_model: filter_dto) -> "prototype":
        """Фильтрует данные по DTO и возвращает новый экземпляр prototype."""
        if filter_model is None or not isinstance(filter_model, filter_dto):
            raise arguments_exception("Фильтр должен быть объектом filter_dto", "filter_model")

        filtered = [item for item in self._data if self._match(item, filter_model)]
        return prototype(filtered)

    def _match(self, item: Any, filter_model: filter_dto) -> bool:
        """Проверяет, соответствует ли доменная сущность всем заданным условиям фильтра."""
        if item is None:
            return False

        # Универсальное сравнение любых полей фильтра с одноименными свойствами модели
        for prop_name in self._get_properties(filter_model):
            if prop_name in self._CONTROL_FIELDS:
                continue

            filter_val = getattr(filter_model, prop_name, None)
            if filter_val is None or (isinstance(filter_val, str) and not filter_val.strip()):
                continue

            if not hasattr(item, prop_name):
                return False

            item_val = getattr(item, prop_name, None)
            if item_val is None:
                return False

            ignore_case = isinstance(item_val, UUID) or isinstance(filter_val, UUID)
            if not self._compare_text(str(item_val), str(filter_val), filter_model.filter_type, ignore_case=ignore_case):
                return False

        # Фильтрация по периоду (если заданы даты)
        if filter_model.start_period is not None or filter_model.end_period is not None:
            item_period = getattr(item, "period", None)
            if not isinstance(item_period, datetime):
                return False
            if filter_model.start_period is not None and item_period < filter_model.start_period:
                return False
            if filter_model.end_period is not None and item_period > filter_model.end_period:
                return False

        # Поиск во вложенных структурах
        if filter_model.nested is not None:
            if not self._match_nested(item, filter_model.nested, set()):
                return False

        return True

    def _compare_text(
        self,
        value: str,
        pattern: str,
        mode: filter_type_enum,
        ignore_case: bool = False
    ) -> bool:
        """Сравнивает строку со значением фильтра в режиме EQUALS или LIKE."""
        left = value.strip()
        right = pattern.strip()

        if mode == filter_type_enum.LIKE:
            return right.lower() in left.lower()

        if ignore_case:
            return left.lower() == right.lower()
        return left == right

    def _get_properties(self, obj: Any) -> list[str]:
        """Извлекает имена публичных @property объекта по цепочке наследования."""
        props = []
        for cls in type(obj).__mro__:
            for name, attr in cls.__dict__.items():
                if isinstance(attr, property) and not name.startswith("_") and name not in props:
                    props.append(name)
        return props

    def _match_nested(self, obj: Any, nested_filter: filter_dto, visited: set[int]) -> bool:
        """Рекурсивно ищет совпадение по фильтру во вложенных свойствах и списках."""
        for prop_name in self._get_properties(obj):
            val = getattr(obj, prop_name, None)
            if isinstance(val, abstract_reference):
                if self._check_nested_candidate(val, nested_filter, visited):
                    return True
            elif isinstance(val, (list, tuple)):
                for element in val:
                    if isinstance(element, abstract_reference):
                        if self._check_nested_candidate(element, nested_filter, visited):
                            return True
        return False

    def _check_nested_candidate(
        self,
        candidate: abstract_reference,
        nested_filter: filter_dto,
        visited: set[int]
    ) -> bool:
        """Проверяет вложенный объект."""
        if id(candidate) in visited:
            return False

        next_visited = set(visited)
        next_visited.add(id(candidate))

        if self._match(candidate, nested_filter):
            return True
        return self._match_nested(candidate, nested_filter, next_visited)