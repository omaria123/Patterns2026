import pytest
from Src.Models.range_model import range_model
from Src.Core.exception import arguments_exception


def test_success_range_model_default_init():
    """Проверка создания единицы измерения по умолчанию (без аргументов)."""
    # Act
    unit = range_model()

    # Assert
    assert unit.name == ""
    assert unit.conversion_factor == 1
    assert unit.base_unit == unit


def test_success_range_model_init_name_only():
    """Проверка создания единицы измерения только с указанием имени."""
    # Act
    unit = range_model("грамм")

    # Assert
    assert unit.name == "грамм"
    assert unit.conversion_factor == 1
    assert unit.base_unit == unit


def test_success_range_model_init_with_factor():
    """Проверка создания базовой единицы с явным указанием коэффициента 1."""
    # Act
    base_range = range_model("грамм", 1)

    # Assert
    assert base_range.name == "грамм"
    assert base_range.conversion_factor == 1
    assert base_range.base_unit == base_range


def test_success_range_model_init_with_all_params():
    """Проверка создания производной единицы со всеми параметрами (кг ссылается на грамм)."""
    # Arrange
    base_range = range_model("грамм", 1)

    # Act
    kg_range = range_model("кг", 1000, base_range)

    # Assert
    assert kg_range.name == "кг"
    assert kg_range.conversion_factor == 1000
    assert kg_range.base_unit == base_range


def test_success_range_model_float_factor():
    """Проверка создания единицы с дробным коэффициентом пересчета (миллиграмм)."""
    # Arrange
    gram = range_model("грамм", 1)

    # Act (в 1 миллиграмме 0.001 грамма)
    mg = range_model("миллиграмм", 0.001, gram)

    # Assert
    assert mg.conversion_factor == 0.001


def test_success_range_model_demonstrate_conversion_work():
    """
    Демонстрация работы с моделью единиц измерения (пункт 10 ТЗ):
    пересчет произвольного веса из производной единицы (кг) в базовую (граммы).
    """
    # Arrange: создаем базовый грамм и килограмм с коэффициентом 1000
    gram = range_model("грамм", 1)
    kg = range_model("кг", 1000, gram)

    # Входные данные: 3.8 килограмма продукта
    weight_in_kg = 3.8

    # Act: пересчитываем килограммы в базовые граммы по формуле
    weight_in_grams = weight_in_kg * kg.conversion_factor

    # Assert: проверяем, что 3.8 кг превратились ровно в 3800 грамм
    assert weight_in_grams == 3800.0


def test_throw_arguments_exception_range_model_zero_factor():
    """Проверка выброса исключения arguments_exception при коэффициенте равном 0."""
    # Act & Assert
    with pytest.raises(arguments_exception):
        range_model("кг", 0)


def test_throw_arguments_exception_range_model_negative_factor():
    """Проверка выброса исключения arguments_exception при отрицательном коэффициенте."""
    # Act & Assert
    with pytest.raises(arguments_exception):
        range_model("кг", -100)


def test_throw_arguments_exception_range_model_invalid_factor_type():
    """Проверка выброса исключения arguments_exception, если коэффициент передан строкой."""
    # Act & Assert
    with pytest.raises(arguments_exception):
        range_model("кг", "тысяча")

