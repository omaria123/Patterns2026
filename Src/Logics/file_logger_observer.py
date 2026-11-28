import os

from Src.Core.abstract_class import abstract_reference
from Src.Core.abstract_observer import abstract_observer
from Src.Core.event_type import event_type
from Src.Core.exception import arguments_exception
from Src.Dtos.log_type_enum import log_type_enum
from Src.Models.log_model import log_model


class file_logger_observer(abstract_observer):
    """Наблюдатель для записи событий системы в файл."""

    def __init__(self, file_path: str = "logs.log") -> None:
        """Инициализация файлового логгера."""
        if not isinstance(file_path, str) or not file_path.strip():
            raise arguments_exception("Путь к файлу лога должен быть непустой строкой", "file_path")

        self._file_path = file_path.strip()
        parent_dir = os.path.dirname(self._file_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

    @property
    def file_path(self) -> str:
        """Путь к файлу лога."""
        return self._file_path

    def _to_log_model(self, event: event_type, params: abstract_reference | None = None) -> log_model:
        """Преобразует событие в модель log_model."""
        if isinstance(params, log_model):
            return params

        if params is not None:
            details = params.name if getattr(params, "name", "") else type(params).__name__
            return log_model.create(
                subsystem="System",
                log_type=log_type_enum.INFO,
                message=f"Событие '{event.value}': {details} ({params.id})",
                event=event
            )

        return log_model.create(
            subsystem="System",
            log_type=log_type_enum.INFO,
            message=f"Выполнено событие '{event.value}'",
            event=event
        )

    def handler(self, event: event_type, params: abstract_reference | None = None) -> None:
        """Записывает событие в файл лога."""
        if not isinstance(event, event_type):
            raise arguments_exception("Тип события должен быть элементом event_type", "event")

        entry = self._to_log_model(event, params)
        period_str = entry.period.strftime("%Y-%m-%d %H:%M:%S")
        line = f"{period_str} | {entry.log_type.value:<5} | {entry.subsystem} | {entry.event.value} | {entry.message}\n"

        with open(self._file_path, "a", encoding="utf-8") as file:
            file.write(line)

    def read_logs(self) -> list[str]:
        """Читает строки из файла лога."""
        if not os.path.exists(self._file_path):
            return []
        with open(self._file_path, "r", encoding="utf-8") as file:
            return [line.rstrip("\n") for line in file if line.strip()]

    def __eq__(self, other: object) -> bool:
        """Сравнивает логгеры по пути к файлу."""
        if not isinstance(other, file_logger_observer):
            return False
        return self._file_path == other._file_path