import pytest
from enum import Enum
from Src.Dtos.report_type_enum import report_type_enum
from Src.Dtos.report_result_dto import report_result_dto
from Src.Logics.report_factory import report_factory
from Src.Logics.text_report import text_report
from Src.Models.recipe_model import recipe_model
from Src.Models.recipe_row_model import recipe_row_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.group_model import group_model
from Src.Models.range_model import range_model
from Src.Core.exception import arguments_exception
from Src.Logics.csv_report import csv_report
from Src.Logics.markdown_report import markdown_report
from Src.Logics.xml_report import xml_report
from Src.Logics.html_report import html_report
from Src.Models.settings_model import settings_model


@pytest.fixture
def sample_recipe():
    """Фикстура для сквозного теста."""
    grocery = group_model("Бакалея")
    gram = range_model("грамм", 1)
    piece = range_model("штука", 1)

    pizza = nomenclature_model("Пицца", "Пицца Маргарита", grocery, piece)
    flour = nomenclature_model("Мука", "Мука", grocery, gram)
    row = recipe_row_model.create(flour, brutto=160, netto=160)

    return recipe_model.create("Пицца", pizza, rows=[row])


def test_success_report_factory_create_txt():
    """Положительный тест: фабрика возвращает правильный инстанс text_report по типу TXT."""
    # Arrange
    factory = report_factory()

    # Act
    report = factory.create(report_type_enum.TXT)

    # Assert
    assert report is not None
    assert isinstance(report, text_report)


def test_throw_exception_report_factory_invalid_types():
    """Тест на исключение: передача неподдерживаемого типа вызывает arguments_exception."""
    # Arrange
    factory = report_factory()

    class unsupported_enum(Enum):
        CSV = 2

    # Act & Assert: неподдерживаемый элемент enum
    with pytest.raises(arguments_exception):
        factory.create(unsupported_enum.CSV)

    # Act & Assert: передача None
    with pytest.raises(arguments_exception):
        factory.create(None)

    # Act & Assert: передача строки
    with pytest.raises(arguments_exception):
        factory.create("txt")


def test_success_report_factory_build_integration_flow(sample_recipe):
    """Сквозной тест: получение отчета из фабрики и успешное формирование текста."""
    # Arrange
    factory = report_factory()
    report = factory.create(report_type_enum.TXT)

    # Act
    result = report.build(sample_recipe)

    # Assert
    assert isinstance(result, report_result_dto)
    assert result.text != ""
    assert "Мука" in result.text
    assert "160" in result.text

def test_success_report_factory_creates_all_types():
    """Проверка фабрики: корректное создание генераторов для всех 5 поддерживаемых форматов."""
    # Arrange
    factory = report_factory()

    # Act & Assert
    assert isinstance(factory.create(report_type_enum.TXT), text_report)
    assert isinstance(factory.create(report_type_enum.CSV), csv_report)
    assert isinstance(factory.create(report_type_enum.MARKDOWN), markdown_report)
    assert isinstance(factory.create(report_type_enum.XML), xml_report)
    assert isinstance(factory.create(report_type_enum.HTML), html_report)


def test_success_report_factory_create_default_markdown():
    """Проверка метода create_default(): создание отчета по умолчанию из настроек (Markdown)."""
    # Arrange: создаем настройки с форматом markdown
    settings = settings_model()
    settings.response_format = report_type_enum.MARKDOWN
    factory = report_factory(settings)

    # Act
    report = factory.create_default()

    # Assert
    assert report is not None
    assert isinstance(report, markdown_report)


def test_success_report_factory_create_default_csv():
    """Проверка метода create_default(): переключение формата по умолчанию на CSV."""
    # Arrange: меняем настройку на CSV
    settings = settings_model()
    settings.response_format = report_type_enum.CSV
    factory = report_factory(settings)

    # Act
    report = factory.create_default()

    # Assert
    assert isinstance(report, csv_report)


def test_throw_exception_report_factory_invalid_argument():
    """Проверка выброса исключения arguments_exception при передаче некорректного типа."""
    # Arrange
    factory = report_factory()

    # Act & Assert
    with pytest.raises(arguments_exception):
        factory.create("не_enum")

    with pytest.raises(arguments_exception):
        factory.create(None)