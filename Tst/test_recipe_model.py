import pytest
from Src.Models.recipe_model import recipe_model
from Src.Models.recipe_row_model import recipe_row_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.group_model import group_model
from Src.Models.range_model import range_model
from Src.Core.exception import arguments_exception


@pytest.fixture
def sample_data():
    """Фикстура для создания тестовых моделей пиццы и ингредиентов."""
    dairy = group_model("Молочная продукция")
    sauces = group_model("Соусы")
    dishes = group_model("Готовые блюда")

    gram = range_model("грамм", 1)
    piece = range_model("штука", 1)

    pizza = nomenclature_model("Пицца Маргарита", "Пицца Маргарита 30 см", dishes, piece)
    cheese = nomenclature_model("Сыр Моцарелла", "Сыр Моцарелла", dairy, gram)
    sauce = nomenclature_model("Томатный соус", "Соус томатный", sauces, gram)

    # Две строки рецепта
    row_cheese = recipe_row_model.create(cheese, brutto=120, netto=115)
    row_sauce = recipe_row_model.create(sauce, brutto=90, netto=85)

    return pizza, row_cheese, row_sauce


def test_success_recipe_model_create_and_weights(sample_data):
    """Проверка создания рецепта и подсчета суммарного веса брутто и нетто."""
    # Arrange
    pizza, row_cheese, row_sauce = sample_data

    # Act
    recipe = recipe_model.create(
        name="Пицца Маргарита",
        target_item=pizza,
        rows=[row_cheese, row_sauce]
    )

    # Assert: 120 + 90 = 210 (брутто), 115 + 85 = 200 (нетто)
    assert recipe.name == "Пицца Маргарита"
    assert recipe.target_item == pizza
    assert len(recipe.rows) == 2
    assert recipe.brutto_weight == 210
    assert recipe.netto_weight == 200


def test_success_recipe_model_weights_recalculated_on_add_row(sample_data):
    """Проверка пересчета брутто и нетто при добавлении нового ингредиента."""
    # Arrange: создаем рецепт с сыром и соусом (брутто = 210, нетто = 200)
    pizza, row_cheese, row_sauce = sample_data
    recipe = recipe_model.create("Пицца", pizza, [row_cheese, row_sauce])

    # Подготавливаем новый ингредиент (базилик: брутто 5, нетто 4)
    greens = group_model("Зелень")
    gram = range_model("грамм", 1)
    basil = nomenclature_model("Базилик", "Базилик свежий", greens, gram)
    row_basil = recipe_row_model.create(basil, brutto=5, netto=4)

    # Act: добавляем базилик в рецепт
    add_result = recipe.add_row(row_basil)

    # Assert: вес должен автоматически увеличиться (210 + 5 = 215, 200 + 4 = 204)
    assert add_result is True
    assert len(recipe.rows) == 3
    assert recipe.brutto_weight == 215
    assert recipe.netto_weight == 204


def test_success_recipe_model_weights_recalculated_on_delete_row(sample_data):
    """Проверка пересчета брутто и нетто при удалении ингредиента из рецепта."""
    # Arrange: создаем рецепт с двумя ингредиентами
    pizza, row_cheese, row_sauce = sample_data
    recipe = recipe_model.create("Пицца", pizza, [row_cheese, row_sauce])

    # Act: удаляем соус из рецепта (брутто 90, нетто 85)
    delete_result = recipe.delete_row(row_sauce)

    # Assert: вес уменьшился, остался только сыр (брутто 120, нетто 115)
    assert delete_result is True
    assert len(recipe.rows) == 1
    assert recipe.brutto_weight == 120
    assert recipe.netto_weight == 115


def test_throw_exception_recipe_model_invalid_row_type(sample_data):
    """Проверка ошибки при попытке добавить в рецепт объект неверного типа."""
    # Arrange
    pizza, _, _ = sample_data
    recipe = recipe_model("Пицца", pizza)

    # Act & Assert
    with pytest.raises(arguments_exception):
        recipe.add_row("Не_строка_рецепта")


def test_throw_exception_recipe_model_invalid_target_item():
    """Проверка ошибки при установке некорректного целевого блюда."""
    # Arrange
    recipe = recipe_model("Пицца")

    # Act & Assert
    with pytest.raises(arguments_exception):
        recipe.target_item = 12345

def test_success_recipe_model_composite_dish_with_recursion():
    """
    Проверка составной технологической карты и рекурсии:
    Пицца 'Маргарита' включает в себя полуфабрикат 'Тесто для пиццы'.
    """
    # Arrange 1: Создаем полуфабрикат 'Тесто' и его рецепт
    grocery = group_model("Бакалея")
    dishes = group_model("Блюда")
    gram = range_model("грамм", 1)
    piece = range_model("штука", 1)

    flour = nomenclature_model("Мука", "Мука пшеничная", grocery, gram)
    water = nomenclature_model("Вода", "Вода питьевая", grocery, gram)
    dough_item = nomenclature_model("Тесто для пиццы", "Тесто полуфабрикат", dishes, gram)

    row_flour = recipe_row_model.create(flour, brutto=160, netto=160)
    row_water = recipe_row_model.create(water, brutto=90, netto=90)

    # Рецепт полуфабриката: вес брутто = 250, нетто = 250
    recipe_dough = recipe_model.create("Рецепт теста", dough_item, rows=[row_flour, row_water])

    # Arrange 2: Создаем начинку пиццы (сыр: брутто 120, нетто 115)
    dairy = group_model("Молочка")
    cheese = nomenclature_model("Сыр", "Сыр Моцарелла", dairy, gram)
    row_cheese = recipe_row_model.create(cheese, brutto=120, netto=115)

    pizza_item = nomenclature_model("Пицца Маргарита", "Пицца 30 см", dishes, piece)

    # Act: создаем составной рецепт пиццы
    recipe_pizza = recipe_model.create(
        name="Пицца Маргарита",
        target_item=pizza_item,
        rows=[row_cheese],               # прямая начинка 
        sub_recipes=[recipe_dough]        # вложенный рецепт теста 
    )

    # Assert: 
    # Брутто: 120 (сыр) + 250 (тесто) = 370
    # Нетто: 115 + 250 = 365
    assert len(recipe_pizza.rows) == 1
    assert len(recipe_pizza.sub_recipes) == 1
    assert recipe_pizza.brutto_weight == 370
    assert recipe_pizza.netto_weight == 365


def test_success_recipe_model_recursion_updates_when_sub_recipe_changes():
    """Проверка: если изменить рецепт теста (полуфабриката), вес пиццы пересчитывается автоматически."""
    # Arrange: рецепт теста 
    grocery = group_model("Бакалея")
    dishes = group_model("Блюда")
    gram = range_model("грамм", 1)

    flour = nomenclature_model("Мука", "Мука", grocery, gram)
    row_flour = recipe_row_model.create(flour, brutto=160, netto=160)
    recipe_dough = recipe_model.create("Тесто", flour, rows=[row_flour])

    # Пицца, куда входит тесто (вес пиццы = 160 г)
    pizza_item = nomenclature_model("Пицца", "Пицца", dishes, gram)
    recipe_pizza = recipe_model.create("Пицца", pizza_item, sub_recipes=[recipe_dough])
    assert recipe_pizza.netto_weight == 160

    # Act: шеф-повар добавил в рецепт теста 10 г дрожжей
    yeast = nomenclature_model("Дрожжи", "Дрожжи", grocery, gram)
    row_yeast = recipe_row_model.create(yeast, brutto=10, netto=10)
    recipe_dough.add_row(row_yeast)

    # Assert: вес пиццы вырос за счет рекурсии (160 + 10 = 170)
    assert recipe_pizza.netto_weight == 170

