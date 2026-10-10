from Src.Core.abstract_class import abstract_reference
from Src.Core.exception import arguments_exception
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.recipe_row_model import recipe_row_model


class recipe_model(abstract_reference):
    """
    Модель технологической карты (рецепта).
    Содержит целевое готовое блюдо или полуфабрикат,
    список строк-ингредиентов и динамически вычисляет общий вес Брутто и Нетто.
    Поддерживает составные рецепты.
    """

    def __init__(
        self,
        name: str = "",
        target_item: nomenclature_model | None = None
    ) -> None:
        """
        Инициализатор технологической карты.

        Параметры:
            name: Наименование рецепта.
            target_item: Номенклатура готового изделия или полуфабриката.
        """
        super().__init__()

        self._target_item: nomenclature_model | None = None
        self._rows: list[recipe_row_model] = []
        self._sub_recipes: list["recipe_model"] = []  # Вложенные рецепты 

        if name:
            self.name = name
        if target_item is not None:
            self.target_item = target_item

    @property
    def target_item(self) -> nomenclature_model | None:
        """Геттер готового изделия или полуфабриката рецепта."""
        return self._target_item

    @target_item.setter
    def target_item(self, value: nomenclature_model) -> None:
        """Сеттер готового изделия с проверкой типа."""
        if not isinstance(value, nomenclature_model):
            raise arguments_exception("Целевое изделие должно быть объектом типа nomenclature_model", "target_item")
        self._target_item = value


    @property
    def rows(self) -> list[recipe_row_model]:
        """Список строк рецепта."""
        return list(self._rows)

    def add_row(self, row: recipe_row_model) -> bool:
        """
        Добавление строки ингредиента в рецепт.
        """
        if not isinstance(row, recipe_row_model):
            raise arguments_exception("Строка рецепта должна быть объектом типа recipe_row_model")

        # Защита от добавления одной и той же строки дважды
        if row in self._rows:
            return False

        self._rows.append(row)
        return True

    def delete_row(self, row: recipe_row_model) -> bool:
        """
        Исключение строки ингредиента из рецепта.
        """
        if row not in self._rows:
            return False

        self._rows.remove(row)
        return True

    @property
    def sub_recipes(self) -> list["recipe_model"]:
        """Список вложенных технологических карт (полуфабрикатов)."""
        return list(self._sub_recipes)

    def add_sub_recipe(self, recipe: "recipe_model") -> bool:
        """
        Добавление вложенного рецепта.
        """
        if not isinstance(recipe, recipe_model):
            raise arguments_exception("Вложенный рецепт должен быть объектом типа recipe_model")

        if recipe in self._sub_recipes or recipe == self:
            return False

        self._sub_recipes.append(recipe)
        return True

    def delete_sub_recipe(self, recipe: "recipe_model") -> bool:
        """
        Удаление вложенного рецепта.
        """
        if recipe not in self._sub_recipes:
            return False

        self._sub_recipes.remove(recipe)
        return True

    @property
    def brutto_weight(self) -> int | float:
        """
        Общий вес брутто рецепта.
        Сумма брутто прямых строк + брутто всех вложенных рецептов.
        """
        direct_brutto = sum(row.brutto for row in self._rows)
        sub_brutto = sum(sub.brutto_weight for sub in self._sub_recipes)
        return round(direct_brutto + sub_brutto, 3)

    @property
    def netto_weight(self) -> int | float:
        """
        Общий вес нетто рецепта.
        Сумма нетто прямых строк + нетто всех вложенных рецептов.
        """
        direct_netto = sum(row.netto for row in self._rows)
        sub_netto = sum(sub.netto_weight for sub in self._sub_recipes)
        return round(direct_netto + sub_netto, 3)

    @staticmethod
    def create(
        name: str,
        target_item: nomenclature_model,
        rows: list[recipe_row_model] | None = None,
        sub_recipes: list["recipe_model"] | None = None
    ) -> "recipe_model":
        """
        Фабричный метод для создания готовой технологической карты.
        """
        recipe = recipe_model(name=name, target_item=target_item)
        if rows:
            for row in rows:
                recipe.add_row(row)
        if sub_recipes:
            for sub in sub_recipes:
                recipe.add_sub_recipe(sub)
        return recipe