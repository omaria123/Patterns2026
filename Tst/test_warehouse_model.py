from Src.Models.warehouse_model import warehouse_model
import pytest
from Src.Core.exception import arguments_exception

def test_success_warehouse_model_create():
    """
    <summary>
    Проверка корректного создания модели склада с наименованием.
    </summary>
    """
    # Arrange
    name = "Основной склад цеха"

    # Act
    warehouse = warehouse_model(name)

    # Assert
    assert warehouse.name == name
    assert warehouse.id is not None

def test_success_warehouse_model_address():
    """Проверка установки корректного адреса склада."""
    # Arrange
    warehouse = warehouse_model("Основной склад")
    expected_address = "г. Москва, ул. Ленина, д. 1"

    # Act
    warehouse.address = expected_address

    # Assert
    assert warehouse.address == expected_address


def test_throw_arguments_exception_warehouse_invalid_address():
    """Проверка ошибки при передаче пустого адреса или некорректного типа."""
    # Arrange
    warehouse = warehouse_model("Основной склад")

    # Act & Assert (пустая строка)
    with pytest.raises(arguments_exception):
        warehouse.address = "   "

    # Act & Assert (число вместо строки)
    with pytest.raises(arguments_exception):
        warehouse.address = 12345