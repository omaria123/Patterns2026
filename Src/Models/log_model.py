from datetime import datetime

from Src.Core.abstract_class import abstract_reference
from Src.Core.event_type import event_type
from Src.Core.exception import arguments_exception
from Src.Dtos.log_type_enum import log_type_enum


class log_model(abstract_reference):
    """Доменная модель записи журнала логирования."""

    def __init__(
        self,
        subsystem: str = "System",
        log_type: log_type_enum | str = log_type_enum.INFO,
        message: str = "",
        event: event_type | str = event_type.WEB_REQUEST,
        period: datetime | str | None = None
    ) -> None:
        """Инициализирует запись лога с валидацией параметров."""
        super().__init__()
        self._period: datetime = datetime.now()
        self._subsystem: str = ""
        self._log_type: log_type_enum = log_type_enum.INFO
        self._event: event_type = event_type.WEB_REQUEST
        self._message: str = ""

        self.subsystem = subsystem
        self.log_type = log_type
        self.event = event
        if message:
            self.message = message
        if period is not None:
            self.period = period
        self.name = f"[{self._log_type.value}] {self._subsystem}"[:50]

    @property
    def period(self) -> datetime:
        """Возвращает дату и время события."""
        return self._period

    @period.setter
    def period(self, value: datetime | str) -> None:
        """Устанавливает дату и время события."""
        if isinstance(value, datetime):
            self._period = value
            return
        if isinstance(value, str):
            try:
                self._period = datetime.fromisoformat(value.strip())
                return
            except ValueError:
                raise arguments_exception(f"Некорректный формат даты: '{value}'", "period")
        raise arguments_exception("Период должен быть datetime или ISO-строкой", "period")

    @property
    def subsystem(self) -> str:
        """Возвращает название подсистемы, сформировавшей запись."""
        return self._subsystem

    @subsystem.setter
    def subsystem(self, value: str) -> None:
        """Устанавливает название подсистемы."""
        if not isinstance(value, str) or not value.strip():
            raise arguments_exception("Название подсистемы должно быть непустой строкой", "subsystem")
        self._subsystem = value.strip()

    @property
    def log_type(self) -> log_type_enum:
        """Возвращает уровень логирования."""
        return self._log_type

    @log_type.setter
    def log_type(self, value: log_type_enum | str) -> None:
        """Устанавливает уровень логирования."""
        if isinstance(value, log_type_enum):
            self._log_type = value
            return
        if isinstance(value, str):
            cleaned = value.strip().upper()
            for item in log_type_enum:
                if item.value == cleaned or item.name == cleaned:
                    self._log_type = item
                    return
        raise arguments_exception(f"Некорректный тип сообщения лога: '{value}'", "log_type")

    @property
    def event(self) -> event_type:
        """Возвращает тип системного события."""
        return self._event

    @event.setter
    def event(self, value: event_type | str) -> None:
        """Устанавливает тип системного события."""
        if isinstance(value, event_type):
            self._event = value
            return
        if isinstance(value, str):
            cleaned = value.strip().lower()
            for item in event_type:
                if item.value == cleaned or item.name.lower() == cleaned:
                    self._event = item
                    return
        raise arguments_exception(f"Некорректный тип события: '{value}'", "event")

    @property
    def message(self) -> str:
        """Возвращает текст сообщения лога."""
        return self._message

    @message.setter
    def message(self, value: str) -> None:
        """Устанавливает текст сообщения лога."""
        if not isinstance(value, str) or not value.strip():
            raise arguments_exception("Сообщение лога должно быть непустой строкой", "message")
        self._message = value.strip()

    @staticmethod
    def create(subsystem: str, log_type: log_type_enum,message: str,event: event_type = event_type.WEB_REQUEST,
        period: datetime | None = None) -> "log_model":
        """Метод создания заполненной записи лога."""
        return log_model(
            subsystem=subsystem,
            log_type=log_type,
            message=message,
            event=event,
            period=period
        )