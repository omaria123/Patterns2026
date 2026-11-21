from datetime import datetime

from Src.Core.abstract_class import abstract_reference
from Src.Core.exception import arguments_exception
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.warehouse_model import warehouse_model


class transaction_model(abstract_reference):
    """
    Модель складской транзакции (движения номенклатуры).
    Положительное значение value означает поступление, отрицательное — списание.
    """

    def __init__(
        self,
        name: str = "",
        warehouse: warehouse_model | None = None,
        nomenclature: nomenclature_model | None = None,
        unit: range_model | None = None,
        value: int | float = 1,
        period: datetime | str | None = None
    ) -> None:
        """Инициализирует модель складской транзакции с валидацией полей."""
        super().__init__()
        self._warehouse: warehouse_model | None = None
        self._nomenclature: nomenclature_model | None = None
        self._unit: range_model | None = None
        self._value: float = 0.0
        self._period: datetime = datetime.now()

        if name:
            self.name = name
        if warehouse is not None:
            self.warehouse = warehouse
        if nomenclature is not None:
            self.nomenclature = nomenclature
        if unit is not None:
            self.unit = unit
        self.value = value
        if period is not None:
            self.period = period

    @property
    def warehouse(self) -> warehouse_model | None:
        """Возвращает склад, по которому прошла транзакция."""
        return self._warehouse

    @warehouse.setter
    def warehouse(self, value: warehouse_model) -> None:
        """Устанавливает склад транзакции."""
        if not isinstance(value, warehouse_model):
            raise arguments_exception("Склад должен быть объектом warehouse_model", "warehouse")
        self._warehouse = value

    @property
    def nomenclature(self) -> nomenclature_model | None:
        """Возвращает номенклатуру транзакции."""
        return self._nomenclature

    @nomenclature.setter
    def nomenclature(self, value: nomenclature_model) -> None:
        """Устанавливает номенклатуру транзакции."""
        if not isinstance(value, nomenclature_model):
            raise arguments_exception("Номенклатура должна быть объектом nomenclature_model", "nomenclature")
        self._nomenclature = value

    @property
    def unit(self) -> range_model | None:
        """Возвращает единицу измерения транзакции."""
        return self._unit

    @unit.setter
    def unit(self, value: range_model) -> None:
        """Устанавливает единицу измерения транзакции."""
        if not isinstance(value, range_model):
            raise arguments_exception("Единица измерения должна быть объектом range_model", "unit")
        self._unit = value

    @property
    def value(self) -> float:
        """Возвращает количество движения."""
        return self._value

    @value.setter
    def value(self, source: int | float) -> None:
        """Устанавливает количество движения с запретом нулевого значения."""
        if not isinstance(source, (int, float)) or isinstance(source, bool):
            raise arguments_exception("Количество транзакции должно быть числом", "value")
        if source == 0:
            raise arguments_exception("Количество транзакции не может быть равно нулю", "value")
        self._value = float(source)

    @property
    def period(self) -> datetime:
        """Возвращает дату и время проведения транзакции."""
        return self._period

    @period.setter
    def period(self, value: datetime | str) -> None:
        """Устанавливает дату и время транзакции."""
        if isinstance(value, datetime):
            self._period = value
            return
        if isinstance(value, str):
            try:
                self._period = datetime.fromisoformat(value.strip())
                return
            except ValueError:
                raise arguments_exception(f"Некорректный формат даты транзакции: '{value}'", "period")
        raise arguments_exception("Период должен быть datetime или ISO-строкой", "period")

    @staticmethod
    def create(
        warehouse: warehouse_model,
        nomenclature: nomenclature_model,
        unit: range_model,
        value: int | float,
        period: datetime | str | None = None,
        name: str = ""
    ) -> "transaction_model":
        """Фабричный метод создания складской транзакции."""
        op_name = name.strip() if name else f"{'Приход' if value > 0 else 'Списание'}: {nomenclature.name}"
        return transaction_model(
            name=op_name[:50],
            warehouse=warehouse,
            nomenclature=nomenclature,
            unit=unit,
            value=value,
            period=period
        )