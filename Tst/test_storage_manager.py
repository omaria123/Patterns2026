import pytest
from Src.Logics.storage_manager import storage_manager
from Src.Models.settings_model import settings_model
from Src.Models.warehouse_model import warehouse_model
from Src.Models.range_model import range_model
from Src.Core.exception import arguments_exception


@pytest.fixture(autouse=True)
def clean_storage():
    """Сброс состояния хранилища перед каждым тестом."""
    storage_manager.clear()
    yield
    storage_manager.clear()


def test_success_storage_manager_is_singleton():
    """Проверка, что storage_manager реализует паттерн Синглтон."""
    # Arrange & Act
    storage1 = storage_manager()
    storage2 = storage_manager()

    # Assert
    assert storage1 is storage2
    assert storage1 == storage2


def test_success_storage_manager_first_start_generates_data():
    """Проверка генерации базовых данных при первом старте (is_first_start = True)."""
    # Arrange
    settings = settings_model()
    settings.is_first_start = True

    # Act
    storage = storage_manager()
    result = storage.convert(settings)

    # Assert
    assert result is True
    assert storage.is_loaded is True
    assert len(storage.units) == 5
    assert len(storage.groups) == 6
    assert len(storage.warehouses) == 2
    assert len(storage.nomenclature) == 9

    # Проверяем наличие ключевых позиций
    item_names = [item.name for item in storage.nomenclature.values()]
    assert "Мука пшеничная" in item_names
    assert "Сыр Моцарелла" in item_names
    assert "Базилик свежий" in item_names
    assert "Томатный соус" in item_names
    assert "Пицца Маргарита" in item_names
    assert "Коробка для пиццы" in item_names

    # Добавляем проверку рецептов:
    assert len(storage.recipes) == 1


def test_success_storage_manager_first_start_disabled():
    """Проверка, что при is_first_start = False данные не генерируются."""
    # Arrange
    settings = settings_model()
    settings.is_first_start = False

    # Act
    storage = storage_manager()
    result = storage.convert(settings)

    # Assert
    assert result is False
    assert storage.is_loaded is False
    assert len(storage.units) == 0
    assert len(storage.groups) == 0
    assert len(storage.warehouses) == 0
    assert len(storage.nomenclature) == 0

    # Добавляем проверку, что рецептов 0:
    assert len(storage.recipes) == 0


def test_success_storage_manager_uniqueness_control():
    """Проверка контроля уникальности: дубликат объекта с тем же ID не добавляется."""
    # Arrange
    storage = storage_manager()
    wh = warehouse_model(name="Центральный склад", address="ул. Мира, 1")

    # Act
    first_add = storage.add(wh)
    duplicate_add = storage.add(wh)

    # Assert
    assert first_add is True
    assert duplicate_add is False
    assert len(storage.warehouses) == 1


def test_success_storage_manager_item_relations():
    """Проверка корректности связей созданной номенклатуры с группой и единицей измерения."""
    # Arrange
    settings = settings_model()
    settings.is_first_start = True

    # Act
    storage = storage_manager()
    storage.convert(settings)

    # Находим базилик и пиццу
    basil = next(item for item in storage.nomenclature.values() if item.name == "Базилик свежий")
    pizza = next(item for item in storage.nomenclature.values() if item.name == "Пицца Маргарита")

    # Assert: проверяем связи
    assert basil.group.name == "Овощи и зелень"
    assert basil.unit.name == "грамм"

    assert pizza.group.name == "Готовые блюда"
    assert pizza.unit.name == "штука"


def test_throw_exception_storage_manager_add_invalid_type():
    """Проверка выброса исключения arguments_exception при добавлении некорректного типа объекта."""
    # Arrange
    storage = storage_manager()

    # Act & Assert
    with pytest.raises(arguments_exception):
        storage.add("Непонятная строка вместо модели")


def test_success_storage_manager_load_calls_convert():
    """Проверка метода load(): он должен вызывать convert() и завершаться успешно."""
    # Arrange
    settings = settings_model()
    settings.is_first_start = True

    # Act
    storage = storage_manager()
    storage.load()

    # Assert: проверяем, что флаг загорелся и номенклатура появилась
    assert storage.is_loaded is True
    assert len(storage.nomenclature) > 0


def test_success_storage_manager_data_property():
    """Проверка свойства data: оно должно содержать все 4 словаря коллекций."""
    # Arrange & Act
    storage = storage_manager()

    # Assert
    assert "warehouses" in storage.data
    assert "units" in storage.data
    assert "groups" in storage.data
    assert "nomenclature" in storage.data

    assert "recipes" in storage.data

def test_success_storage_manager_pizza_recipe_presence_and_weights():
    """Проверка наличия рецепта пиццы в хранилище и корректности расчета брутто/нетто."""
    # Arrange
    settings = settings_model()
    settings.is_first_start = True

    # Act
    storage = storage_manager()
    storage.convert(settings)

    # Достаем созданный рецепт пиццы из хранилища
    recipe = next(r for r in storage.recipes.values() if "Пицца Маргарита" in r.name)

    # Assert: проверяем привязку к целевому блюду и количество строк ингредиентов
    assert recipe.target_item.name == "Пицца Маргарита"
    assert len(recipe.rows) == 8

    # Assert: проверяем расчет суммарного веса Брутто и Нетто
    # 160 + 2.5 + 10 + 3 + 90 + 120 + 5 + 1 = 391.5 (брутто)
    # 160 + 2.5 + 10 + 3 + 85 + 115 + 4 + 1 = 380.5 (нетто)
    assert recipe.brutto_weight == 391.5
    assert recipe.netto_weight == 380.5