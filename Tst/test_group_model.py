from Src.Models.group_model import group_model


def test_success_group_model_create():
    """
    Проверка корректного создания модели группы номенклатуры.
    """
    # Arrange
    name = "Мясная продукция"

    # Act
    group = group_model(name)

    # Assert
    assert group.name == name
    assert group.id is not None