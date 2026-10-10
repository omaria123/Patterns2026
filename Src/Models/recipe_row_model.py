from Src.Core.abstract_class import abstract_reference
from Src.Core.exception import arguments_exception
from Src.Models.nomenclature_model import nomenclature_model


class recipe_row_model(abstract_reference):
    """
    Модель строки технологической карты.
    Содержит ссылку на номенклатуру, а также вес брутто и нетто в граммах.
    """

    def __init__(
        self,
        nomenclature: nomenclature_model | None = None,
        brutto: int | float = 0,
        netto: int | float = 0
    ) -> None:
        """
        Инициализатор строки технологической карты.

        Параметры:
            nomenclature: Ссылка на номенклатуру (ингредиент).
            brutto: Вес брутто (в граммах, строго больше 0).
            netto: Вес нетто (в граммах, строго больше 0 и не больше брутто).
        """
        super().__init__()

        self._nomenclature: nomenclature_model | None = None
        self._brutto: int | float = 0
        self._netto: int | float = 0

        if nomenclature is not None:
            self.nomenclature = nomenclature
        if brutto > 0:
            self.brutto = brutto
        if netto > 0:
            self.netto = netto


    @property
    def nomenclature(self) -> nomenclature_model | None:
        """Геттер номенклатуры (ингредиента)."""
        return self._nomenclature

    @nomenclature.setter
    def nomenclature(self, value: nomenclature_model) -> None:
        """
        Сеттер номенклатуры с проверкой типа.
        """
        if not isinstance(value, nomenclature_model):
            raise arguments_exception("Ингредиент должен быть объектом типа nomenclature_model", "nomenclature")
        self._nomenclature = value


    @property
    def brutto(self) -> int | float:
        """Геттер веса брутто (в граммах)."""
        return self._brutto

    @brutto.setter
    def brutto(self, value: int | float) -> None:
        """
        Сеттер веса брутто с проверкой на положительное число.
        """
        if not isinstance(value, (int, float)):
            raise arguments_exception("Вес брутто должен быть числом", "brutto")
        if value <= 0:
            raise arguments_exception("Вес брутто должен быть больше 0", "brutto")

        self._brutto = value


    @property
    def netto(self) -> int | float:
        """Геттер веса нетто (в граммах)."""
        return self._netto

    @netto.setter
    def netto(self, value: int | float) -> None:
        """
        Сеттер веса нетто с проверкой: число > 0 и netto <= brutto.
        """
        if not isinstance(value, (int, float)):
            raise arguments_exception("Вес нетто должен быть числом", "netto")
        if value <= 0:
            raise arguments_exception("Вес нетто должен быть больше 0", "netto")
        if self._brutto > 0 and value > self._brutto:
            raise arguments_exception("Вес нетто не может превышать вес брутто", "netto")

        self._netto = value

    @staticmethod
    def create(
        nomenclature: nomenclature_model,
        brutto: int | float,
        netto: int | float
    ) -> "recipe_row_model":
        """
        Фабричный метод для быстрого создания валидной строки рецепта.
        """
        row = recipe_row_model()
        row.nomenclature = nomenclature
        row.brutto = brutto
        row.netto = netto
        return row