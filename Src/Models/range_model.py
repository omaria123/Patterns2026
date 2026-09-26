from __future__ import annotations
from Src.Core.abstract_class import abstract_reference
from Src.Core.exception import arguments_exception


class range_model(abstract_reference):
    """
    Модель единицы измерения.
    Содержит наименование, коэффициент пересчета и ссылку на базовую единицу измерения.
    """

    def __init__(
        self,
        name: str = "",
        conversion_factor: int | float = 1,
        base_unit: range_model | None = None
    ) -> None:
        """
        Инициализатор сущности 'Единица измерения'.

        Параметр name: Наименование единицы измерения (например, 'грамм', 'кг').
        Параметр conversion_factor: Коэффициент пересчета к базовой единице (по умолчанию 1).
        Параметр base_unit: Ссылка на базовую единицу измерения (если None, то базовая единица — сама эта сущность).
        """
        super().__init__()

        self._conversion_factor: int | float = 1
        self._base_unit: range_model | None = None

        if name:
            self.name = name
        self.conversion_factor = conversion_factor
        self.base_unit = base_unit if base_unit is not None else self

    @property
    def conversion_factor(self) -> int | float:
        """Геттер для получения коэффициента пересчета к базовой единице."""
        return self._conversion_factor

    @conversion_factor.setter
    def conversion_factor(self, value: int | float) -> None:
        """
        Сеттер для установки коэффициента пересчета с валидацией.

        Параметр value: Положительное число (коэффициент).
        raises arguments_exception: Если передано не число или значение меньше либо равно нулю.
        """
        if not isinstance(value, (int, float)):
            raise arguments_exception("Коэффициент пересчета должен быть числом", "conversion_factor")

        if value <= 0:
            raise arguments_exception("Коэффициент пересчета должен быть больше нуля", "conversion_factor")

        self._conversion_factor = value

    @property
    def base_unit(self) -> range_model | None:
        """Геттер для получения ссылки на базовую единицу измерения."""
        return self._base_unit

    @base_unit.setter
    def base_unit(self, value: range_model | None) -> None:
        """
        Сеттер для установки базовой единицы измерения.

        Параметр value: Объект range_model или None.
        raises arguments_exception: Если передан объект другого типа.
        """
        if value is not None and not isinstance(value, range_model):
            raise arguments_exception("Базовая единица должна быть объектом типа range_model", "base_unit")

        self._base_unit = value