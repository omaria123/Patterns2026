from Src.Core.abstract_class import abstract_reference
from Src.Core.exception import arguments_exception
from Src.Models.group_model import group_model
from Src.Models.range_model import range_model


class nomenclature_model(abstract_reference):
    """
    Модель номенклатуры (товара, сырья, полуфабриката или блюда).
    Включает краткое имя (до 50 симв.), полное имя (до 255 симв.),
    а также ссылки на группу номенклатуры и единицу измерения.
    """

    def __init__(
        self,
        name: str = "",
        full_name: str = "",
        group: group_model | None = None,
        unit: range_model | None = None
    ) -> None:
        """
        Инициализатор сущности 'Номенклатура'.

        Параметры:
            name: Краткое наименование товара (до 50 символов).
            full_name: Полное наименование товара (до 255 символов).
            group: Группа, к которой принадлежит номенклатура (объект group_model).
            unit: Единица измерения номенклатуры (объект range_model).
        """
        super().__init__()

        self._full_name: str = ""
        self._group: group_model | None = None
        self._unit: range_model | None = None

        if name:
            self.name = name
        if full_name:
            self.full_name = full_name
        if group is not None:
            self.group = group
        if unit is not None:
            self.unit = unit

    @property
    def full_name(self) -> str:
        """Геттер для получения полного наименования номенклатуры."""
        return self._full_name

    @full_name.setter
    def full_name(self, value: str) -> None:
        """
        Сеттер для установки полного наименования с валидацией длины (до 255 символов).

        Параметр value: Строка полного наименования.
        arguments_exception: Если передана не строка, строка пустая или длиннее 255 символов.
        """
        if not isinstance(value, str):
            raise arguments_exception("Полное наименование должно быть строкой", "full_name")

        cleaned = value.strip()
        if not cleaned:
            raise arguments_exception("Полное наименование не может быть пустым", "full_name")

        if len(cleaned) > 255:
            raise arguments_exception("Полное наименование не может превышать 255 символов", "full_name")

        self._full_name = cleaned

    @property
    def group(self) -> group_model | None:
        """Геттер для получения группы номенклатуры."""
        return self._group

    @group.setter
    def group(self, value: group_model | None) -> None:
        """
        Сеттер для установки группы номенклатуры.

        Параметр value: Объект класса group_model или None.
        arguments_exception: Если передан объект неверного типа.
        """
        if value is not None and not isinstance(value, group_model):
            raise arguments_exception("Группа должна быть объектом типа group_model", "group")

        self._group = value

    @property
    def unit(self) -> range_model | None:
        """Геттер для получения единицы измерения номенклатуры."""
        return self._unit

    @unit.setter
    def unit(self, value: range_model | None) -> None:
        """
        Сеттер для установки единицы измерения.

        Параметр value: Объект класса range_model или None.
        arguments_exception: Если передан объект неверного типа.
        """
        if value is not None and not isinstance(value, range_model):
            raise arguments_exception("Единица измерения должна быть объектом типа range_model", "unit")

        self._unit = value