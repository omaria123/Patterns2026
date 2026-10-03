from Src.Core.abstract_class import abstract_reference
from Src.Core.exception import arguments_exception


class warehouse_model(abstract_reference):
    """
    Модель склада для хранения номенклатуры.
    Наследует базовые атрибуты id и name от abstract_reference,
    а также содержит физический адрес.
    """

    def __init__(self, name: str = "", address: str = "") -> None:
        """
        Инициализатор сущности 'Склад'.
        Параметры:
            name: Наименование склада (строка до 50 символов).
            address: Физический адрес склада.
        """
        super().__init__()
        self._address: str = ""

        if name:
            self.name = name
        if address:
            self.address = address

    @property
    def address(self) -> str:
        """Адрес склада."""
        return self._address

    @address.setter
    def address(self, value: str):
        """Сеттер адреса склада."""
        if not isinstance(value, str) or not value.strip():
            raise arguments_exception("Некорректный адрес")
        self._address = value.strip()