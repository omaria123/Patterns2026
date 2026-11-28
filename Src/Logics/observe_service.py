from Src.Core.abstract_class import abstract_reference
from Src.Core.abstract_observer import abstract_observer
from Src.Core.event_type import event_type
from Src.Core.exception import arguments_exception


class observe_service:
    """Диспетчер событий для шаблона проектирования Наблюдатель."""

    _handlers: list[abstract_observer] = []

    @classmethod
    def handlers(cls) -> list[abstract_observer]:
        """Возвращает копию списка текущих наблюдателей."""
        return list(cls._handlers)

    @classmethod
    def add(cls, handler: abstract_observer) -> None:
        """Подписывает наблюдателя на получение событий."""
        if handler is None or not isinstance(handler, abstract_observer):
            raise arguments_exception("Наблюдатель должен наследовать abstract_observer", "handler")

        if handler not in cls._handlers:
            cls._handlers.append(handler)

    @classmethod
    def delete(cls, handler: abstract_observer) -> None:
        """Отписывает наблюдателя от получения событий."""
        if handler is None or not isinstance(handler, abstract_observer):
            raise arguments_exception("Наблюдатель должен наследовать abstract_observer", "handler")

        if handler in cls._handlers:
            cls._handlers.remove(handler)

    @classmethod
    def clear(cls) -> None:
        """Очищает список всех наблюдателей."""
        cls._handlers.clear()

    @classmethod
    def create(cls, event: event_type, params: abstract_reference | None = None) -> None:
        """Рассылает событие всем подписанным наблюдателям."""
        if not isinstance(event, event_type):
            raise arguments_exception("Тип события должен быть элементом event_type", "event")
        if params is not None and not isinstance(params, abstract_reference):
            raise arguments_exception("Параметры события должны наследовать abstract_reference", "params")

        for handler in list(cls._handlers):
            if handler is not None:
                handler.handler(event, params)