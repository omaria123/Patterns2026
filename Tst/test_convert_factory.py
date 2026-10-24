import json
from uuid import uuid4
import pytest
import os

from Src.Logics.convert_factory import convert_factory
from Src.Models.group_model import group_model
from Src.Models.range_model import range_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.recipe_model import recipe_model
from Src.Models.recipe_row_model import recipe_row_model
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager


def test_success_convert_factory_primitive_and_list():
    """Проверка конвертации примитивных типов и списков через фабрику."""
    # Arrange
    factory = convert_factory()

    # Act
    res_str = factory.convert("Тестовая строка")
    res_num = factory.convert(42.5)
    res_list = factory.convert(["Пицца", 100, True])

    # Assert
    assert res_str == "Тестовая строка"
    assert res_num == 42.5
    assert res_list == ["Пицца", 100, True]


def test_success_convert_factory_flat_model():
    """Проверка конвертации простой доменной сущности (group_model)."""
    # Arrange
    factory = convert_factory()
    group = group_model("Бакалея")

    # Act
    result = factory.convert(group)

    # Assert
    assert isinstance(result, dict)
    assert result["name"] == "Бакалея"
    assert result["id"] == str(group.id)


def test_success_convert_factory_composite_nomenclature():
    """Проверка составной сущности: номенклатура со ссылками на группу и единицу измерения."""
    # Arrange
    factory = convert_factory()
    grocery = group_model("Бакалея")
    gram = range_model("грамм", 1)
    flour = nomenclature_model("Мука", "Мука пшеничная в/с", grocery, gram)

    # Act
    result = factory.convert(flour)

    # Assert
    assert result["name"] == "Мука"
    assert result["full_name"] == "Мука пшеничная в/с"
    assert result["group"]["name"] == "Бакалея"
    assert result["unit"]["name"] == "грамм"


def test_success_convert_factory_recursion_range_model_board_case():
    """
    Проверка рекурсии
    """
    # Arrange
    factory = convert_factory()
    kg = range_model.create_kilogram()

    # Act
    result = factory.convert(kg)

    # Assert
    assert result["name"] == "килограмм"
    assert result["conversion_factor"] == 1000
    assert result["base_unit"] is not None
    assert result["base_unit"]["name"] == "грамм"
    assert result["base_unit"]["conversion_factor"] == 1
    # Зацикленная ссылка грамма на самого себя безопасно оборвана
    assert result["base_unit"]["base_unit"] is None


def test_success_convert_factory_recipe_with_rows_and_json_dumps():
    """
    Конвертация рецепта пиццы со строками ингредиентов
    и проверка сериализации в JSON-строку через json.dumps.
    """
    # Arrange
    factory = convert_factory()

    dairy = group_model("Молочная продукция")
    gram = range_model("грамм", 1)
    piece = range_model("штука", 1)

    pizza = nomenclature_model("Пицца", "Пицца Маргарита", dairy, piece)
    cheese = nomenclature_model("Сыр", "Сыр Моцарелла", dairy, gram)

    row = recipe_row_model.create(cheese, brutto=120, netto=115)
    recipe = recipe_model.create("Пицца Маргарита", target_item=pizza, rows=[row])

    # Act 1: Конвертация фабрикой в словарь
    dict_result = factory.convert(recipe)

    # Assert 1: Проверка структуры словаря
    assert dict_result["name"] == "Пицца Маргарита"
    assert dict_result["target_item"]["name"] == "Пицца"
    assert len(dict_result["rows"]) == 1
    assert dict_result["rows"][0]["brutto"] == 120
    assert dict_result["rows"][0]["netto"] == 115
    assert dict_result["rows"][0]["nomenclature"]["name"] == "Сыр"

    # Act 2: Сериализация словаря в стандартную JSON-строку
    json_string = json.dumps(dict_result, ensure_ascii=False)

    # Assert 2: json.dumps отработал успешно, строка валидна
    assert isinstance(json_string, str)
    assert "Пицца Маргарита" in json_string
    assert "Сыр Моцарелла" in json_string

def test_success_export_domain_models_to_json_files():
    """
    Тест и генерация JSON-файлов.
    Проверяет конвертацию списков моделей 
    и формирует итоговые JSON-файлы коллекций в директории Json/.
    """
    # Arrange: загружаем хранилище с тестовыми данными
    sm = settings_manager()
    if not sm.is_loaded:
        sm.load()

    storage = storage_manager()
    if not storage.is_loaded:
        storage.convert(sm.settings)

    factory = convert_factory()
    output_dir = "Json"
    os.makedirs(output_dir, exist_ok=True)

    # Коллекции списков объектов каждой модели
    collections = {
        "recipes.json": list(storage.recipes.values()),
        "nomenclature.json": list(storage.nomenclature.values()),
        "units.json": list(storage.units.values()),
        "warehouses.json": list(storage.warehouses.values()),
        "groups.json": list(storage.groups.values()),
    }

    # Act & Assert
    for file_name, items in collections.items():
        converted_list = factory.convert(items)

        # Проверяем, что конвертировался именно список и он не пустой
        assert isinstance(converted_list, list)
        assert len(converted_list) > 0

        # Сохраняем в файл 
        file_path = os.path.join(output_dir, file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(converted_list, f, ensure_ascii=False, indent=2)

        assert os.path.exists(file_path)