from abc import ABC, abstractmethod
from typing import Any


class abstract_convertor(ABC):
    """
    Базовый абстрактный класс для всех конверторов.
    Задает единый контракт преобразования значения поля в словарь {field: value}.
    """

    @abstractmethod
    def convert(self, field: str, obj: Any, visited: set | None = None) -> dict:
        """
        Преобразовать переданный объект в словарь.
        """
        pass