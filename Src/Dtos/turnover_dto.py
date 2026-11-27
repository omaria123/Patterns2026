from Src.Core.abstract_class import abstract_reference
from Src.Core.exception import arguments_exception
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.warehouse_model import warehouse_model


class turnover_dto(abstract_reference):
    """DTO-модель строки оборотно-сальдовой ведомости (ОСВ)."""

    def __init__(
        self,
        warehouse: warehouse_model | None = None,
        nomenclature: nomenclature_model | None = None,
        unit: range_model | None = None,
        opening_balance: float = 0.0,
        income: float = 0.0,
        outcome: float = 0.0
    ) -> None:
        """Инициализирует строку ОСВ с расчетом конечного остатка."""
        super().__init__()
        self._warehouse = warehouse
        self._nomenclature = nomenclature
        self._unit = unit
        self._opening_balance = round(float(opening_balance), 3)
        self._income = round(float(income), 3)
        self._outcome = round(float(outcome), 3)

        if nomenclature is not None:
            self.name = nomenclature.name

    @property
    def opening_balance(self) -> float:
        """Возвращает начальный остаток на начало периода."""
        return self._opening_balance

    @opening_balance.setter
    def opening_balance(self, value: float) -> None:
        """Устанавливает начальный остаток."""
        self._opening_balance = round(float(value), 3)

    @property
    def income(self) -> float:
        """Возвращает суммарное поступление за период."""
        return self._income

    @income.setter
    def income(self, value: float) -> None:
        """Устанавливает сумму прихода."""
        self._income = round(float(value), 3)

    @property
    def outcome(self) -> float:
        """Возвращает суммарный расход за период."""
        return self._outcome

    @outcome.setter
    def outcome(self, value: float) -> None:
        """Устанавливает сумму расхода."""
        self._outcome = round(float(value), 3)

    @property
    def warehouse(self) -> warehouse_model | None:
        """Возвращает склад строки ОСВ."""
        return self._warehouse

    @property
    def nomenclature(self) -> nomenclature_model | None:
        """Возвращает номенклатуру строки ОСВ."""
        return self._nomenclature

    @property
    def unit(self) -> range_model | None:
        """Возвращает единицу измерения строки ОСВ."""
        return self._unit

    @property
    def closing_balance(self) -> float:
        """Возвращает конечный остаток на конец периода."""
        return round(self._opening_balance + self._income - self._outcome, 3)

    @staticmethod
    def create(
        warehouse: warehouse_model,
        nomenclature: nomenclature_model,
        unit: range_model,
        opening_balance: float,
        income: float,
        outcome: float
    ) -> "turnover_dto":
        """Фабричный метод создания строки ОСВ с проверкой входных моделей."""
        if not isinstance(warehouse, warehouse_model):
            raise arguments_exception("Склад должен быть объектом warehouse_model", "warehouse")
        if not isinstance(nomenclature, nomenclature_model):
            raise arguments_exception("Номенклатура должна быть объектом nomenclature_model", "nomenclature")
        if not isinstance(unit, range_model):
            raise arguments_exception("Единица измерения должна быть объектом range_model", "unit")

        return turnover_dto(warehouse, nomenclature, unit, opening_balance, income, outcome)