import pytest
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.group_model import group_model
from Src.Models.range_model import range_model
from Src.Core.exception import arguments_exception


def test_success_nomenclature_model_create_all_parameters():
    """Проверка успешного создания номенклатуры со всеми связанными объектами."""
    # Arrange (Подготовка зависимых моделей и данных)
    group = group_model("Молочная продукция")
    unit = range_model("кг", 1000)
    name = "Сыр Моцарелла"
    full_name = "Сыр Моцарелла для пиццы полутвердый 45% жирности"

    # Act (Создание номенклатуры)
    item = nomenclature_model(
        name=name,
        full_name=full_name,
        group=group,
        unit=unit
    )

    # Assert (Проверка правильности всех полей и связей)
    assert item.name == name
    assert item.full_name == full_name
    assert item.group == group
    assert item.unit == unit
    assert item.id is not None


def test_success_nomenclature_model_default_init():
    """Проверка создания номенклатуры с параметрами по умолчанию."""
    # Act
    item = nomenclature_model()

    # Assert
    assert item.name == ""
    assert item.full_name == ""
    assert item.group is None
    assert item.unit is None


def test_throw_arguments_exception_nomenclature_full_name_too_long():
    """Проверка выброса исключения arguments_exception при превышении длины полного имени (более 255 символов)."""
    # Arrange (Строка длиной 256 символов)
    too_long_name = "Н" * 256

    # Act & Assert
    with pytest.raises(arguments_exception):
        nomenclature_model(full_name=too_long_name)


def test_throw_arguments_exception_nomenclature_full_name_empty():
    """Проверка выброса исключения arguments_exception при пустом полном наименовании."""
    # Arrange & Act & Assert
    with pytest.raises(arguments_exception):
        nomenclature_model(full_name="    ")


def test_throw_arguments_exception_nomenclature_invalid_group_type():
    """Проверка выброса исключения arguments_exception при передаче некорректного типа группы."""
    # Arrange & Act & Assert
    with pytest.raises(arguments_exception):
        nomenclature_model(group="1234")


def test_throw_arguments_exception_nomenclature_invalid_unit_type():
    """Проверка выброса исключения arguments_exception при передаче некорректного типа единицы измерения."""
    # Arrange & Act & Assert
    with pytest.raises(arguments_exception):
        nomenclature_model(unit=12345)

def test_success_nomenclature_model_full_name_max_length_boundary():
    """Проверка граничного значения: полное наименование ровно из 255 символов должно успешно сохраняться."""
    # Arrange: создаем строку ровно из 255 символов
    exact_255_chars = "А" * 255

    # Act
    item = nomenclature_model(full_name=exact_255_chars)

    # Assert
    assert len(item.full_name) == 255
    assert item.full_name == exact_255_chars


def test_success_nomenclature_model_setters_after_init():
    """Проверка изменения свойств номенклатуры через сеттеры после создания объекта."""
    # Arrange
    item = nomenclature_model()
    group = group_model("Бакалея")
    unit = range_model("шт", 1)

    # Act
    item.name = "Сахар"
    item.full_name = "Сахар белый кристаллический"
    item.group = group
    item.unit = unit

    # Assert
    assert item.name == "Сахар"
    assert item.full_name == "Сахар белый кристаллический"
    assert item.group == group
    assert item.unit == unit