import pytest
from Src.Logics.text_report import text_report
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.recipe_model import recipe_model
from Src.Models.recipe_row_model import recipe_row_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.group_model import group_model
from Src.Models.range_model import range_model
from Src.Core.exception import arguments_exception


@pytest.fixture
def sample_recipe():
    """Фикстура: рецепт пиццы с ингредиентами для проверки отчета."""
    grocery = group_model("Бакалея")
    dairy = group_model("Молочка")
    gram = range_model("грамм", 1)
    piece = range_model("штука", 1)

    pizza = nomenclature_model("Пицца", "Пицца Маргарита", grocery, piece)
    flour = nomenclature_model("Мука", "Мука пшеничная", grocery, gram)
    cheese = nomenclature_model("Сыр", "Сыр Моцарелла", dairy, gram)

    row1 = recipe_row_model.create(flour, brutto=160, netto=160)
    row2 = recipe_row_model.create(cheese, brutto=120, netto=115)

    return recipe_model.create("Пицца Маргарита", pizza, rows=[row1, row2])


def test_success_text_report_build(sample_recipe):
    """Проверка генерации текстового отчета: содержит название, разделители и данные."""
    # Arrange
    reporter = text_report()

    # Act
    result = reporter.build(sample_recipe)

    # Assert
    assert isinstance(result, report_result_dto)
    assert result.text != ""
    assert "Пицца Маргарита" in result.text
    assert "|" in result.text
    assert "Мука" in result.text
    assert "160" in result.text


def test_throw_exception_text_report_invalid_source():
    """Проверка ошибки: передача неверного источника данных (не recipe_model)."""
    # Arrange
    reporter = text_report()

    # Act & Assert
    with pytest.raises(arguments_exception):
        reporter.build("Обычная_строка")