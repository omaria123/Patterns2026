from abc import ABC, abstractmethod
from typing import Any
from Src.Core.abstract_convertor import abstract_convertor


class abstract_factory(ABC):
    """
    Базовый абстрактный класс для фабрик.
    Определяет единый контракт подбора нужного конвертора.
    """

    @abstractmethod
    def create(self, obj: Any) -> abstract_convertor:
        """
        Подобрать и вернуть нужный конвертор для объекта.
        """
        pass