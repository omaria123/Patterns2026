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
from Src.Logics.convert_factory import convert_factory

def test_success_deserialize_flat_group_model():
    """Проверка десериализации плоской модели группы номенклатуры."""
    # Arrange: создаем случайный тестовый ID
    factory = deserialize_factory()
    test_id = uuid4()
    data = {
        "type": "Src.Models.group_model.group_model",
        "id": str(test_id),
        "name": "Бакалея"
    }

    # Act
    group = factory.deserialize(data)

    # Assert
    assert isinstance(group, group_model)
    assert group.id == test_id
    assert group.name == "Бакалея"
    assert group.type == "Src.Models.group_model.group_model"


def test_success_deserialize_warehouse_model():
    """Проверка десериализации склада с адресом."""
    # Arrange
    factory = deserialize_factory()
    test_id = uuid4()
    data = {
        "type": "Src.Models.warehouse_model.warehouse_model",
        "id": str(test_id),
        "name": "Центральный склад цеха",
        "address": "г. Москва, ул. Производственная, д. 5"
    }

    # Act
    wh = factory.deserialize(data)

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
        "type": "Src.Models.range_model.range_model",
        "id": str(test_id),
        "name": "грамм",
        "conversion_factor": 1,
        "base_unit": None
    }

    # Act
    unit = factory.deserialize(data)

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
    data1 = {"type": "Src.Models.group_model.group_model", "id": shared_id, "name": "Бакалея"}
    data2 = {"type": "Src.Models.group_model.group_model", "id": shared_id, "name": "Бакалея"}

    # Act
    obj1 = factory.deserialize(data1)
    obj2 = factory.deserialize(data2)

    # Assert
    assert obj1 is obj2
    assert obj1.id == UUID(shared_id)

def test_full_roundtrip_all_data_export_import_and_compare():
    """
    Полный тест 
    Берет все коллекции storage_manager, сериализует в JSON,
    десериализует обратно и по полям сравнивает все доменные модели.
    """
    # 1. Инициализируем хранилище
    sm = settings_manager()
    if not sm.is_loaded:
        sm.load()

    storage = storage_manager()
    if not storage.is_loaded:
        storage.convert(sm.settings)

    c_factory = convert_factory()
    d_factory = deserialize_factory(storage=storage)

    # 2. Сериализуем все коллекции storage_manager
    exported_data = {
        key: c_factory.convert(list(collection.values()))
        for key, collection in storage.data.items()
    }

    # 3. Десериализуем обратно через deserialize_factory
    restored_data = {
        key: d_factory.deserialize(items)
        for key, items in exported_data.items()
    }

    # 4. Сравниваем:
    # Склады 
    assert len(restored_data["warehouses"]) == len(storage.warehouses)
    for wh in restored_data["warehouses"]:
        orig = storage.warehouses[wh.id]
        assert wh.id == orig.id
        assert wh.name == orig.name
        assert wh.address == orig.address
        assert wh.type == orig.type

    # Единицы измерения 
    assert len(restored_data["units"]) == len(storage.units)
    for u in restored_data["units"]:
        orig = storage.units[u.id]
        assert u.id == orig.id
        assert u.name == orig.name
        assert u.conversion_factor == orig.conversion_factor
        assert u.base_unit.name == orig.base_unit.name
        assert u.type == orig.type

    # Группы номенклатуры 
    assert len(restored_data["groups"]) == len(storage.groups)
    for g in restored_data["groups"]:
        orig = storage.groups[g.id]
        assert g.id == orig.id
        assert g.name == orig.name
        assert g.type == orig.type

    # Номенклатура
    assert len(restored_data["nomenclature"]) == len(storage.nomenclature)
    for item in restored_data["nomenclature"]:
        orig = storage.nomenclature[item.id]
        assert item.id == orig.id
        assert item.name == orig.name
        assert item.full_name == orig.full_name
        assert item.group.name == orig.group.name
        assert item.unit.name == orig.unit.name
        assert item.type == orig.type

    # Рецепты 
    assert len(restored_data["recipes"]) == len(storage.recipes)
    for r in restored_data["recipes"]:
        orig = storage.recipes[r.id]
        assert r.id == orig.id
        assert r.name == orig.name
        assert r.target_item.name == orig.target_item.name
        assert len(r.rows) == len(orig.rows)
        assert r.brutto_weight == orig.brutto_weight
        assert r.netto_weight == orig.netto_weight
        assert r.type == orig.type

def test_throw_exception_deserialize_unknown_type():
    """Проверка ошибки при невозможности определить модель."""
    # Arrange
    factory = deserialize_factory()

    # Act & Assert
    with pytest.raises(arguments_exception):
        factory.deserialize({"type": "Invalid.Unknown.Model", "name": "Тест"})