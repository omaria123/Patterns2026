from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID
from Src.Core.abstract_class import abstract_reference


class abstract_service(ABC):
    """Абстрактный базовый класс сервисного слоя для работы с доменными сущностями."""

    @abstractmethod
    def get_domains(self) -> list[str]:
        """Возвращает список доступных доменных коллекций."""
        pass

    @abstractmethod
    def get_list(self, model_cls: type) -> list:
        """Возвращает список всех сущностей указанного типа."""
        pass

    @abstractmethod
    def get_by_id(self, model_cls: type, entity_id: UUID) -> Any:
        """Возвращает доменную сущность по типу и идентификатору."""
        pass

    @abstractmethod
    def add(self, item: abstract_reference) -> bool:
        """Добавляет доменную сущность в хранилище."""
        pass

    @abstractmethod
    def update(self, entity_id: UUID, item: abstract_reference) -> bool:
        """Обновляет существующую доменную сущность с проверкой целостности."""
        pass

    @abstractmethod
    def delete(self, item: abstract_reference) -> bool:
        """Удаляет доменную сущность при отсутствии связанных объектов."""
        pass

    @abstractmethod
    def is_referenced(self, item: abstract_reference) -> bool:
        """Проверяет наличие входящих ссылок на указанную сущность."""
        pass