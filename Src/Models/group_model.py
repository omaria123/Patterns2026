from Src.Core.abstract_class import abstract_reference


class group_model(abstract_reference):
    """
    Модель группы (категории) номенклатуры.
    Наследует базовые атрибуты id и name от abstract_reference.
    """

    def __init__(self, name: str = "") -> None:
        """
        Инициализатор сущности 'Группа номенклатуры'.
        Параметр: Наименование группы (строка до 50 символов).
        """
        super().__init__()
        if name:
            self.name = name