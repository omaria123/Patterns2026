from __future__ import annotations
from datetime import datetime

from Src.Core.abstract_class import abstract_reference
from Src.Core.exception import arguments_exception
from Src.Dtos.filter_type_enum import filter_type_enum


class filter_dto(abstract_reference):
    """
    DTO-модель параметров фильтрации доменных сущностей.
    Поддерживает фильтрацию по наименованию, коду, периоду и вложенным структурам.
    """

    def __init__(
        self,
        name: str = "",
        id: str | None = None,
        filter_type: filter_type_enum | str = filter_type_enum.EQUALS,
        nested: filter_dto | None = None,
        start_period: datetime | str | None = None,
        end_period: datetime | str | None = None
    ) -> None:
        """Инициализирует DTO фильтрации с валидацией входных параметров."""
        super().__init__()
        self._id = None
        self._filter_type: filter_type_enum = filter_type_enum.EQUALS
        self._nested: filter_dto | None = None
        self._start_period: datetime | None = None
        self._end_period: datetime | None = None

        self.name = name
        if id is not None:
            self.id = id
        self.filter_type = filter_type
        if nested is not None:
            self.nested = nested
        if start_period is not None:
            self.start_period = start_period
        if end_period is not None:
            self.end_period = end_period

    @property
    def name(self) -> str:
        """Возвращает строку фильтра по наименованию."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Устанавливает фильтр по наименованию."""
        if not isinstance(value, str):
            raise arguments_exception("Наименование для фильтрации должно быть строкой", "name")
        cleaned = value.strip()
        if len(cleaned) > 50:
            raise arguments_exception("Наименование для фильтрации не может превышать 50 символов", "name")
        self._name = cleaned

    @property
    def id(self):
        """Возвращает идентификатор для фильтрации."""
        return self._id

    @id.setter
    def id(self, value) -> None:
        """Устанавливает идентификатор для фильтрации."""
        if value is None or value == "":
            self._id = None
            return
        self._id = str(value).strip()

    @property
    def filter_type(self) -> filter_type_enum:
        """Возвращает режим сравнения при фильтрации."""
        return self._filter_type

    @filter_type.setter
    def filter_type(self, value: filter_type_enum | str) -> None:
        """Устанавливает режим фильтрации с поддержкой строкового значения."""
        if isinstance(value, filter_type_enum):
            self._filter_type = value
            return

        if isinstance(value, str):
            cleaned = value.strip().lower()
            for item in filter_type_enum:
                if item.value == cleaned or item.name.lower() == cleaned:
                    self._filter_type = item
                    return
            raise arguments_exception(f"Неподдерживаемый тип фильтрации: '{value}'", "filter_type")

        raise arguments_exception("Тип фильтрации должен быть строкой или filter_type_enum", "filter_type")

    @property
    def nested(self) -> filter_dto | None:
        """Возвращает вложенный фильтр для поиска по дочерним сущностям."""
        return self._nested

    @nested.setter
    def nested(self, value: filter_dto | None) -> None:
        """Устанавливает вложенный фильтр."""
        if value is not None and not isinstance(value, filter_dto):
            raise arguments_exception("Вложенный фильтр должен быть объектом filter_dto", "nested")
        self._nested = value

    @property
    def start_period(self) -> datetime | None:
        """Возвращает начало периода фильтрации."""
        return self._start_period

    @start_period.setter
    def start_period(self, value: datetime | str | None) -> None:
        """Устанавливает дату начала периода."""
        self._start_period = self._parse_datetime(value, "start_period")

    @property
    def end_period(self) -> datetime | None:
        """Возвращает конец периода фильтрации."""
        return self._end_period

    @end_period.setter
    def end_period(self, value: datetime | str | None) -> None:
        """Устанавливает дату конца периода."""
        self._end_period = self._parse_datetime(value, "end_period")

    def _parse_datetime(self, value: datetime | str | None, field: str) -> datetime | None:
        """Преобразует дату из строки ISO или проверяет объект datetime."""
        if value is None or value == "":
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.strip())
            except ValueError:
                raise arguments_exception(f"Некорректный формат даты: '{value}'", field)
        raise arguments_exception("Дата должна быть объектом datetime или ISO-строкой", field)