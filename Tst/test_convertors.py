from datetime import datetime, date
from uuid import uuid4
import pytest

from Src.Core.exception import arguments_exception
from Src.Logics.basic_convertor import basic_convertor
from Src.Logics.datetime_convertor import datetime_convertor
from Src.Logics.reference_convertor import reference_convertor
from Src.Models.group_model import group_model

# ТЕСТЫ: basic_convertor
def test_success_basic_convertor_string():
    """Проверка корректной конвертации строкового значения в словарь."""
    # Arrange
    convertor = basic_convertor()

    # Act
    result = convertor.convert("name", "Маргарита")

    # Assert
    assert result == {"name": "Маргарита"}


def test_success_basic_convertor_numeric():
    """Проверка конвертации целых и вещественных чисел."""
    # Arrange
    convertor = basic_convertor()

    # Act
    int_res = convertor.convert("count", 10)
    float_res = convertor.convert("weight", 250.75)

    # Assert
    assert int_res == {"count": 10}
    assert float_res == {"weight": 250.75}


def test_success_basic_convertor_uuid():
    """Проверка автоматического преобразования UUID в строку."""
    # Arrange
    convertor = basic_convertor()
    test_uuid = uuid4()

    # Act
    result = convertor.convert("id", test_uuid)

    # Assert
    assert result == {"id": str(test_uuid)}


def test_success_basic_convertor_none_and_bool():
    """Проверка конвертации булевых значений и None."""
    # Arrange
    convertor = basic_convertor()

    # Act
    bool_res = convertor.convert("is_active", True)
    none_res = convertor.convert("description", None)

    # Assert
    assert bool_res == {"is_active": True}
    assert none_res == {"description": None}


def test_throw_exception_basic_convertor_empty_field():
    """Проверка выброса arguments_exception при пустом имени поля."""
    # Arrange
    convertor = basic_convertor()

    # Act & Assert
    with pytest.raises(arguments_exception):
        convertor.convert("   ", "значение")


def test_throw_exception_basic_convertor_unsupported_type():
    """Проверка выброса arguments_exception при передаче сложного типа (списка)."""
    # Arrange
    convertor = basic_convertor()

    # Act & Assert
    with pytest.raises(arguments_exception):
        convertor.convert("items", [1, 2, 3])


# ТЕСТЫ: datetime_convertor
def test_success_datetime_convertor_datetime():
    """Проверка преобразования datetime в формат ISO."""
    # Arrange
    convertor = datetime_convertor()
    dt = datetime(2026, 10, 23, 14, 20, 30)

    # Act
    result = convertor.convert("created_at", dt)

    # Assert
    assert result == {"created_at": "2026-10-23T14:20:30"}


def test_success_datetime_convertor_date():
    """Проверка преобразования чистого объекта date в формат ISO."""
    # Arrange
    convertor = datetime_convertor()
    d = date(2026, 10, 23)

    # Act
    result = convertor.convert("report_date", d)

    # Assert
    assert result == {"report_date": "2026-10-23"}


def test_throw_exception_datetime_convertor_invalid_type():
    """Проверка выброса arguments_exception при передаче не-даты."""
    # Arrange
    convertor = datetime_convertor()

    # Act & Assert
    with pytest.raises(arguments_exception):
        convertor.convert("date", "2026-10-23")


# ТЕСТЫ: reference_convertor
def test_success_reference_convertor_isolated():
    """Проверка автономной конвертации модели без участия фабрики."""
    # Arrange
    convertor = reference_convertor()
    group = group_model("Сырье")

    # Act
    result = convertor.convert("group", group)

    # Assert
    assert "group" in result
    assert result["group"]["id"] == str(group.id)
    assert result["group"]["name"] == "Сырье"


def test_throw_exception_reference_convertor_invalid_type():
    """Проверка ошибки при передаче объекта, не наследующего abstract_reference."""
    # Arrange
    convertor = reference_convertor()

    # Act & Assert
    with pytest.raises(arguments_exception):
        convertor.convert("model", {"name": "Не_модель"})