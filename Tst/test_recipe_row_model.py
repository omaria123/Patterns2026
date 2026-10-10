import pytest
from Src.Models.recipe_row_model import recipe_row_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.group_model import group_model
from Src.Models.range_model import range_model
from Src.Core.exception import arguments_exception


@pytest.fixture
def sample_nomenclature():
    """Фикстура для создания тестового ингредиента (сыр)."""
    dairy = group_model("Молочная продукция")
    gram = range_model("грамм", 1)
    return nomenclature_model("Сыр Моцарелла", "Сыр Моцарелла 45%", dairy, gram)


def test_success_recipe_row_model_init_direct(sample_nomenclature):
    """Проверка успешного создания строки рецепта через конструктор."""
    # Arrange & Act
    row = recipe_row_model(sample_nomenclature, brutto=120, netto=115)

    # Assert
    assert row.nomenclature == sample_nomenclature
    assert row.brutto == 120
    assert row.netto == 115
    assert row.id is not None


def test_success_recipe_row_model_factory_create(sample_nomenclature):
    """Проверка создания строки рецепта через фабричный метод create()."""
    # Act
    row = recipe_row_model.create(sample_nomenclature, brutto=160, netto=150)

    # Assert
    assert row.nomenclature == sample_nomenclature
    assert row.brutto == 160
    assert row.netto == 150


def test_throw_exception_recipe_row_model_netto_greater_than_brutto(sample_nomenclature):
    """Проверка ошибки: вес нетто не может быть больше веса брутто."""
    # Arrange
    row = recipe_row_model()
    row.brutto = 100

    # Act & Assert
    with pytest.raises(arguments_exception):
        row.netto = 150  # 150 > 100


def test_throw_exception_recipe_row_model_negative_brutto():
    """Проверка ошибки при отрицательном весе брутто."""
    # Arrange
    row = recipe_row_model()

    # Act & Assert
    with pytest.raises(arguments_exception):
        row.brutto = -10


def test_throw_exception_recipe_row_model_invalid_nomenclature_type():
    """Проверка ошибки при передаче некорректного типа ингредиента."""
    # Arrange
    row = recipe_row_model()

    # Act & Assert
    with pytest.raises(arguments_exception):
        row.nomenclature = "Не_номенклатура"