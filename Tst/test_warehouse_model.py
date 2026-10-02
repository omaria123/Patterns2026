from Src.Models.warehouse_model import warehouse_model


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