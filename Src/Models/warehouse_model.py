from Src.Core.abstract_class import abstract_reference


class warehouse_model(abstract_reference):
    """
    Модель склада для хранения номенклатуры.
    Наследует базовые атрибуты id и name от abstract_reference.
    """

    def __init__(self, name: str = "") -> None:
        """
        Инициализатор сущности 'Склад'.
        Параметр: Наименование склада (строка до 50 символов).
        """
        super().__init__()
        if name:
            self.name = name