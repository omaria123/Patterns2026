from abc import ABC, abstractmethod
from Src.Core.abstract_class import abstract_reference
from Src.Core.event_type import event_type


class abstract_observer(ABC):
    """Абстрактный интерфейс наблюдателя для обработки событий системы."""

    @abstractmethod
    def handler(self, event: event_type, params: abstract_reference | None = None) -> None:
        """Обрабатывает поступившее событие с опциональной доменной моделью параметров."""
        pass