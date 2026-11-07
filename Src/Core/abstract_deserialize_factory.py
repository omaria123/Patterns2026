from abc import ABC, abstractmethod
from typing import Any


class abstract_deserialize_factory(ABC):
    """Абстрактный класс фабрики десериализации данных в модели."""

    @abstractmethod
    def deserialize(self, data: Any, target_type: Any = None) -> Any:
        """Десериализовать данные в доменную модель или список моделей."""
        pass