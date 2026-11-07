import json
from uuid import UUID, uuid4
import pytest

from Src.Core.exception import arguments_exception
from Src.Logics.deserialize_factory import deserialize_factory
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Models.group_model import group_model
from Src.Models.range_model import range_model
from Src.Models.warehouse_model import warehouse_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.recipe_model import recipe_model


def test_success_deserialize_flat_group_model():
    """Проверка десериализации плоской модели группы номенклатуры."""
    # Arrange: создаем случайный тестовый ID
    factory = deserialize_factory()
    test_id = uuid4()
    data = {
        "id": str(test_id),
        "name": "Бакалея"
    }

    # Act
    group = factory.deserialize(data, group_model)

    # Assert
    assert isinstance(group, group_model)
    assert group.id == test_id
    assert group.name == "Бакалея"


def test_success_deserialize_warehouse_model():
    """Проверка десериализации склада с адресом."""
    # Arrange
    factory = deserialize_factory()
    test_id = uuid4()
    data = {
        "id": str(test_id),
        "name": "Центральный склад цеха",
        "address": "г. Москва, ул. Производственная, д. 5"
    }

    # Act
    wh = factory.deserialize(data, warehouse_model)

    # Assert
    assert isinstance(wh, warehouse_model)
    assert wh.id == test_id
    assert wh.name == "Центральный склад цеха"
    assert wh.address == "г. Москва, ул. Производственная, д. 5"


def test_success_deserialize_self_referencing_unit():
    """Проверка восстановления самоссылающейся базовой единицы."""
    # Arrange
    factory = deserialize_factory()
    test_id = uuid4()
    data = {
        "id": str(test_id),
        "name": "грамм",
        "conversion_factor": 1,
        "base_unit": None
    }

    # Act
    unit = factory.deserialize(data, range_model)

    # Assert
    assert isinstance(unit, range_model)
    assert unit.id == test_id
    assert unit.name == "грамм"
    assert unit.conversion_factor == 1
    assert unit.base_unit is unit  


def test_success_deserialize_cache_prevents_duplication():
    """Одинаковые объекты по id переиспользуются в памяти."""
    # Arrange
    factory = deserialize_factory()
    shared_id = str(uuid4())
    data1 = {"id": shared_id, "name": "Бакалея"}
    data2 = {"id": shared_id, "name": "Бакалея"}

    # Act
    obj1 = factory.deserialize(data1, group_model)
    obj2 = factory.deserialize(data2, group_model)

    # Assert
    assert obj1 is obj2
    assert obj1.id == UUID(shared_id)

def test_success_deserialize_and_compare_with_storage_manager():
    """
    Десериализация реальных JSON-файлов
    и сравнение с данными storage_manager.
    """
    from Src.Logics.convert_factory import convert_factory

    # Arrange: загружаем хранилище
    sm = settings_manager()
    if not sm.is_loaded:
        sm.load()

    storage = storage_manager()
    if not storage.is_loaded:
        storage.convert(sm.settings)

    # Синхронизируем файлы Json/ с актуальными ID текущей сессии хранилища
    c_factory = convert_factory()
    collections = {
        "warehouses.json": list(storage.warehouses.values()),
        "units.json": list(storage.units.values()),
        "nomenclature.json": list(storage.nomenclature.values()),
        "recipes.json": list(storage.recipes.values()),
    }
    for file_name, items in collections.items():
        with open(f"Json/{file_name}", "w", encoding="utf-8") as f:
            json.dump(c_factory.convert(items), f, ensure_ascii=False, indent=2)

    factory = deserialize_factory()

    # 1. Проверяем склады
    with open("Json/warehouses.json", "r", encoding="utf-8") as f:
        wh_data = json.load(f)
    deserialized_warehouses = factory.deserialize(wh_data, "warehouse")

    assert len(deserialized_warehouses) == len(storage.warehouses)
    for wh in deserialized_warehouses:
        original = storage.warehouses[wh.id]
        assert wh.id == original.id
        assert wh.name == original.name
        assert wh.address == original.address

    # 2. Проверяем единицы измерения
    with open("Json/units.json", "r", encoding="utf-8") as f:
        units_data = json.load(f)
    deserialized_units = factory.deserialize(units_data, "range")

    assert len(deserialized_units) == len(storage.units)
    for u in deserialized_units:
        original = storage.units[u.id]
        assert u.id == original.id
        assert u.name == original.name
        assert u.conversion_factor == original.conversion_factor
        assert u.base_unit.name == original.base_unit.name

    # 3. Проверяем номенклатуру
    with open("Json/nomenclature.json", "r", encoding="utf-8") as f:
        nom_data = json.load(f)
    deserialized_nomenclature = factory.deserialize(nom_data, "nomenclature")

    assert len(deserialized_nomenclature) == len(storage.nomenclature)
    for item in deserialized_nomenclature:
        original = storage.nomenclature[item.id]
        assert item.id == original.id
        assert item.name == original.name
        assert item.full_name == original.full_name
        assert item.group.name == original.group.name
        assert item.unit.name == original.unit.name

    # 4. Проверяем рецепты
    with open("Json/recipes.json", "r", encoding="utf-8") as f:
        recipe_data = json.load(f)
    deserialized_recipes = factory.deserialize(recipe_data, "recipe")

    assert len(deserialized_recipes) == len(storage.recipes)
    for r in deserialized_recipes:
        original = storage.recipes[r.id]
        assert r.id == original.id
        assert r.name == original.name
        assert r.target_item.name == original.target_item.name
        assert len(r.rows) == len(original.rows)
        assert r.brutto_weight == original.brutto_weight
        assert r.netto_weight == original.netto_weight

def test_throw_exception_deserialize_unknown_type():
    """Проверка ошибки при невозможности определить модель."""
    # Arrange
    factory = deserialize_factory()

    # Act & Assert
    with pytest.raises(arguments_exception):
        factory.deserialize({"unknown_field": 123}, "неизвестный_тип")