from abc import ABC
from uuid import UUID, uuid4
from Src.Core.exception import arguments_exception

class abstract_reference(ABC):
    """
    Базовый абстрактный класс для всех справочных сущностей системы.
    Инкапсулирует уникальный идентификатор и наименование.
    """

    def __init__(self) -> None:
        """Инициализация базовых атрибутов сущности."""
        self._id: UUID = uuid4()
        self._name: str = "" 

    @property
    def id(self) -> UUID:
        """Уникальный идентификатор сущности."""
        return self._id

    @id.setter
    def id(self, value: UUID | str) -> None:
        """Установка идентификатора сущности."""
        if value is None:
            raise arguments_exception("Идентификатор не может быть пустым", "id")

        if isinstance(value, str) and value.strip() == "":
            raise arguments_exception("Строковый идентификатор не может быть пустым", "id")
        self._id = value


    @property
    def name(self) -> str:
        """Наименование сущности."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """
        Установка наименования с валидацией входного значения.

        """
        if not isinstance(value, str):
            raise arguments_exception("Наименование должно быть строкой", "name")

        normalized_value = value.strip()
        if not normalized_value:
            raise arguments_exception("Наименование не может быть пустым", "name")

        if len(normalized_value) > 50:
            raise arguments_exception("Наименование не может превышать 50 символов", "name")

        self._name = normalized_value


    def __eq__(self, other: object) -> bool:
        """Сравнение сущностей по их уникальному идентификатору."""
        if not isinstance(other, abstract_reference):
            return False
        return self._id == other._id

    