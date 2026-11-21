from abc import ABC, abstractmethod
from Src.Core.exception import arguments_exception
from Src.Dtos.filter_dto import filter_dto


class abstract_prototype(ABC):
    """Абстрактный базовый класс шаблона Прототип для фильтрации коллекций доменных моделей."""

    def __init__(self, source: list) -> None:
        """Инициализирует прототип копией переданного списка данных."""
        if not isinstance(source, (list, tuple)):
            raise arguments_exception("Источник данных для прототипа должен быть списком", "source")
        self._data: list = list(source)

    @property
    def data(self) -> list:
        """Возвращает копию текущего набора данных прототипа."""
        return list(self._data)

    @abstractmethod
    def clone(self, filter_model: filter_dto) -> "abstract_prototype":
        """Создает новый экземпляр прототипа с отфильтрованными данными."""
        pass