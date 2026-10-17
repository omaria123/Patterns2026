import pytest
from Src.Logics.csv_report import csv_report
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.recipe_model import recipe_model
from Src.Models.recipe_row_model import recipe_row_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.group_model import group_model
from Src.Models.range_model import range_model
from Src.Core.exception import arguments_exception


@pytest.fixture
def sample_recipe():
    """Тестовый рецепт."""
    grocery = group_model("Бакалея")
    gram = range_model("грамм", 1)
    piece = range_model("штука", 1)

    pizza = nomenclature_model("Пицца", "Пицца Маргарита", grocery, piece)
    flour = nomenclature_model("Мука", "Мука пшеничная", grocery, gram)
    row = recipe_row_model.create(flour, brutto=160, netto=160)
    return recipe_model.create("Пицца Маргарита", pizza, rows=[row])


def test_success_csv_report_build_recipe_binary(sample_recipe):
    """Проверка формирования CSV для рецепта: результат должен быть бинарным."""
    # Arrange
    reporter = csv_report()

    # Act
    result = reporter.build(sample_recipe)

    # Assert (бинарные данные не пустые)
    assert isinstance(result, report_result_dto)
    assert len(result.binary) > 0
    assert result.text == ""

    # Декодируем байты обратно в текст и проверяем структуру
    text_content = bytes(result.binary).decode("utf-8")
    assert "Код;Наименование;Брутто;Нетто" in text_content
    assert "Мука" in text_content
    assert "160" in text_content


def test_throw_exception_csv_report_invalid_source():
    """Проверка ошибки при передаче неверного источника данных."""
    # Arrange
    reporter = csv_report()

    # Act & Assert
    with pytest.raises(arguments_exception):
        reporter.build(12345)