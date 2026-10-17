import pytest
from Src.Logics.xml_report import xml_report
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


def test_success_xml_report_build_recipe_text(sample_recipe):
    """Проверка формирования XML-отчета: текст содержит валидные XML-теги."""
    # Arrange
    reporter = xml_report()

    # Act
    result = reporter.build(sample_recipe)

    # Assert (текстовый структурированный результат)
    assert isinstance(result, report_result_dto)
    assert result.text != ""
    assert '<?xml version="1.0" encoding="UTF-8"?>' in result.text
    assert '<recipe' in result.text
    assert '<ingredients>' in result.text
    assert '<item' in result.text
    assert '</recipe>' in result.text


def test_throw_exception_xml_report_invalid_source():
    """Проверка ошибки при неверном источнике данных."""
    # Arrange
    reporter = xml_report()

    # Act & Assert
    with pytest.raises(arguments_exception):
        reporter.build("не_модель")