from abc import ABC
from uuid import UUID, uuid4


class abstract_reference(ABC):
    """
    Базовый абстрактный класс для всех справочных сущностей системы.
    Инкапсулирует уникальный идентификатор и наименование.
    """

    def __init__(self) -> None:
        """Инициализация базовых атрибутов сущности."""
        self._id: UUID = uuid4()
        self._name: str = ""

    @property
    def id(self) -> UUID:
        """Уникальный идентификатор сущности."""
        return self._id

    @property
    def name(self) -> str:
        """Наименование сущности."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """
        Установка наименования с валидацией входного значения.

        Параметр: строковое название сущности.
        TypeError: если передан объект не строкового типа.
        ValueError: если строка пустая или состоит только из пробелов.
        """
        if not isinstance(value, str):
            raise TypeError("Наименование должно быть строкой.")

        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("Наименование не может быть пустым.")

        self._name = normalized_value