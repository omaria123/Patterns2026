from abc import ABC, abstractmethod


class abstract_has_references(ABC):
    """Абстрактный интерфейс для сущностей, которые ссылаются на другие доменные модели."""

    @abstractmethod
    def get_references(self) -> list:
        """Возвращает список связанных доменных сущностей, на которые ссылается объект."""
        pass