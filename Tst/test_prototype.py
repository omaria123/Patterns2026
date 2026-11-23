import pytest

from Src.Core.exception import arguments_exception
from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.filter_type_enum import filter_type_enum
from Src.Logics.prototype import prototype
from Src.Logics.storage_manager import storage_manager


@pytest.fixture
def loaded_storage():
    """Подготавливает хранилище со стартовыми данными для тестов."""
    storage_manager.clear()
    storage = storage_manager()
    storage.load()
    yield storage
    storage_manager.clear()


def test_success_prototype_equals_and_like_by_name(loaded_storage):
    """Проверка фильтрации номенклатуры по наименованию в режимах EQUALS и LIKE."""
    # Arrange
    items = list(loaded_storage.nomenclature.values())
    proto = prototype(items)

    # Act
    exact_result = proto.clone(filter_dto(name="Мука пшеничная", filter_type=filter_type_enum.EQUALS))
    partial_result = proto.clone(filter_dto(name="мука", filter_type=filter_type_enum.LIKE))

    # Assert (исходный прототип не изменился)
    assert len(proto.data) == len(items)
    assert len(exact_result.data) == 1
    assert exact_result.data[0].name == "Мука пшеничная"
    assert len(partial_result.data) == 1
    assert partial_result.data[0].name == "Мука пшеничная"


def test_success_prototype_filter_by_unique_code_on_groups(loaded_storage):
    """Проверка фильтрации групп по уникальному коду."""
    # Arrange
    groups = list(loaded_storage.groups.values())
    target = next(g for g in groups if g.name == "Бакалея")
    proto = prototype(groups)

    # Act
    result = proto.clone(filter_dto(id=str(target.id), filter_type=filter_type_enum.EQUALS))

    # Assert
    assert len(result.data) == 1
    assert result.data[0] == target


def test_success_prototype_nested_base_unit(loaded_storage):
    """Проверка поиска во вложенных структурах: единица измерения -> базовая единица."""
    # Arrange
    units = list(loaded_storage.units.values())
    proto = prototype(units)
    nested_filter = filter_dto(nested=filter_dto(name="грамм", filter_type=filter_type_enum.EQUALS))

    # Act: должны найтись и "грамм", и "килограмм"
    result = proto.clone(nested_filter)

    # Assert
    names = {u.name for u in result.data}
    assert names == {"грамм", "килограмм"}


def test_success_prototype_nested_and_chain_clone(loaded_storage):
    """Проверка цепочки clone() и глубокого вложенного поиска по группе и базовой единице."""
    # Arrange
    items = list(loaded_storage.nomenclature.values())
    proto = prototype(items)

    # Act
    result = (
        proto
        .clone(filter_dto(nested=filter_dto(name="Бакалея")))
        .clone(filter_dto(nested=filter_dto(name="грамм")))
    )

    # Assert
    names = {i.name for i in result.data}
    assert names == {"Мука пшеничная", "Дрожжи сухие", "Соль"}


def test_success_prototype_nested_in_recipes(loaded_storage):
    """Проверка вложенного поиска внутри строк технологической карты (рецепта)."""
    # Arrange
    recipes = list(loaded_storage.recipes.values())
    proto = prototype(recipes)

    # Act
    result = proto.clone(filter_dto(nested=filter_dto(name="Моцарелла", filter_type=filter_type_enum.LIKE)))

    # Assert
    assert len(result.data) == 1
    assert "Пицца Маргарита" in result.data[0].name


def test_throw_exception_prototype_invalid_arguments():
    """Проверка выброса исключений при некорректных входных аргументах прототипа."""
    # Act & Assert
    with pytest.raises(arguments_exception):
        prototype("не_список")

    proto = prototype([])
    with pytest.raises(arguments_exception):
        proto.clone("не_фильтр")