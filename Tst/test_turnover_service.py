from datetime import datetime
import pytest

from Src.Core.exception import arguments_exception
from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.filter_type_enum import filter_type_enum
from Src.Logics.storage_manager import storage_manager
from Src.Logics.turnover_service import turnover_service


@pytest.fixture
def loaded_storage():
    """Подготавливает хранилище со стартовыми транзакциями."""
    storage_manager.clear()
    storage = storage_manager()
    storage.load()
    yield storage
    storage_manager.clear()


def test_success_turnover_service_all_transactions(loaded_storage):
    """Проверка расчета ОСВ по всем транзакциям без фильтрации."""
    # Arrange
    service = turnover_service(loaded_storage)

    # Act
    rows = service.build(filter_dto())

    # Assert 
    assert len(rows) == 4
    flour_main = next(
        r for r in rows
        if r.warehouse.name == "Центральный склад цеха" and r.nomenclature.name == "Мука пшеничная"
    )
    assert flour_main.opening_balance == 0.0
    assert flour_main.income == 50.0
    assert flour_main.outcome == 12.0
    assert flour_main.closing_balance == 38.0


def test_success_turnover_service_filter_by_nomenclature_and_period(loaded_storage):
    """Проверка ОСВ с фильтром по наименованию и периоду (расчет начального остатка)."""
    # Arrange
    service = turnover_service(loaded_storage)
    flt = filter_dto(
        name="мука",
        filter_type=filter_type_enum.LIKE,
        start_period=datetime(2026, 11, 8, 0, 0),
        end_period=datetime(2026, 11, 20, 23, 59)
    )

    # Act
    rows = service.build(flt)

    # Assert: на Центральном складе поступление 50 был 1 ноября (до start_period -> opening_balance),
    # а списание 12 было 10 ноября (внутри периода -> outcome).
    flour_main = next(r for r in rows if r.warehouse.name == "Центральный склад цеха")
    assert flour_main.opening_balance == 50.0
    assert flour_main.income == 0.0
    assert flour_main.outcome == 12.0
    assert flour_main.closing_balance == 38.0


def test_success_turnover_service_filter_by_warehouse_code(loaded_storage):
    """Проверка ОСВ с фильтрацией по уникальному коду склада."""
    # Arrange
    service = turnover_service(loaded_storage)
    rest_wh = next(w for w in loaded_storage.warehouses.values() if w.name == "Склад ресторана №1")

    # Act
    rows = service.build(filter_dto(unique_code=str(rest_wh.id)))

    # Assert
    assert len(rows) == 2
    assert all(r.warehouse.id == rest_wh.id for r in rows)


def test_throw_exception_turnover_service_invalid_filter(loaded_storage):
    """Проверка ошибки при передаче некорректного фильтра в сервис ОСВ."""
    # Arrange
    service = turnover_service(loaded_storage)

    # Act & Assert
    with pytest.raises(arguments_exception):
        service.build("не_фильтр")