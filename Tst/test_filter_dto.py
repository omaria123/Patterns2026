from datetime import datetime
import pytest

from Src.Core.exception import arguments_exception
from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.filter_type_enum import filter_type_enum


def test_success_filter_dto_default_create():
    """Проверка создания DTO фильтрации со значениями по умолчанию."""
    # Act
    dto = filter_dto()

    # Assert
    assert dto.name == ""
    assert dto.id is None
    assert dto.filter_type == filter_type_enum.EQUALS
    assert dto.nested is None


def test_success_filter_dto_with_nested_and_dates():
    """Проверка создания фильтра с режимом LIKE, вложенным фильтром и периодом."""
    # Arrange
    nested = filter_dto(name="грамм", filter_type="equals")

    # Act
    dto = filter_dto(
        name="Мука",
        filter_type="like",
        nested=nested,
        start_period="2026-11-01T00:00:00",
        end_period="2026-11-20T23:59:59"
    )

    # Assert
    assert dto.name == "Мука"
    assert dto.filter_type == filter_type_enum.LIKE
    assert dto.nested.name == "грамм"
    assert dto.start_period == datetime(2026, 11, 1, 0, 0, 0)
    assert dto.end_period == datetime(2026, 11, 20, 23, 59, 59)


def test_throw_exception_filter_dto_invalid_values():
    """Проверка выброса исключений при некорректном типе фильтрации, дате или вложенном фильтре."""
    # Act & Assert: неизвестный тип фильтра
    with pytest.raises(arguments_exception):
        filter_dto(filter_type="contains")

    # Act & Assert: неверный тип вложенного фильтра
    with pytest.raises(arguments_exception):
        filter_dto(nested="не_фильтр")

    # Act & Assert: неверный формат даты
    with pytest.raises(arguments_exception):
        filter_dto(start_period="не-дата")