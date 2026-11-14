from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID


class abstract_service(ABC):
    """Абстрактный базовый класс сервисного слоя для работы с доменными сущностями."""

    @abstractmethod
    def get_domains(self) -> list[str]:
        """Возвращает список доступных доменных коллекций."""
        pass

    @abstractmethod
    def get_list(self, entity_type: str) -> list:
        """Возвращает список всех сущностей указанного типа."""
        pass

    @abstractmethod
    def get_by_id(self, entity_type: str, entity_id: str | UUID) -> Any:
        """Возвращает доменную сущность по типу и идентификатору."""
        pass

    @abstractmethod
    def create(self, entity_type: str, data: dict) -> Any:
        """Создает и сохраняет новую доменную сущность из словаря данных."""
        pass

    @abstractmethod
    def update(self, entity_type: str, entity_id: str | UUID, data: dict) -> Any:
        """Обновляет существующую доменную сущность с проверкой целостности."""
        pass

    @abstractmethod
    def delete(self, entity_type: str, entity_id: str | UUID) -> bool:
        """Удаляет доменную сущность при отсутствии связанных объектов."""
        pass

    @abstractmethod
    def is_referenced(self, item_or_id: Any) -> bool:
        """Проверяет наличие входящих ссылок на указанную сущность."""
        pass