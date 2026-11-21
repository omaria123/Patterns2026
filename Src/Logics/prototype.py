from datetime import datetime
from typing import Any

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

        # Фильтрация по наименованию
        if filter_model.name:
            item_name = str(getattr(item, "name", ""))
            if not self._compare_text(item_name, filter_model.name, filter_model.filter_type, ignore_case=False):
                return False

        # Фильтрация по уникальному коду (id)
        if filter_model.unique_code:
            item_code = str(getattr(item, "id", ""))
            if not self._compare_text(item_code, filter_model.unique_code, filter_model.filter_type, ignore_case=True):
                return False

        # Фильтрация по периоду 
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