from uuid import uuid4
import pytest

from Src.Core.exception import arguments_exception
from Src.Logics.reference_service import reference_service
from Src.Logics.storage_manager import storage_manager
from Src.Models.group_model import group_model
from Src.Models.warehouse_model import warehouse_model


@pytest.fixture(autouse=True)
def clean_storage():
    """Сброс и инициализация хранилища перед каждым тестом сервиса."""
    storage_manager.clear()
    storage = storage_manager()
    storage.load()
    yield
    storage_manager.clear()


def test_success_reference_service_is_referenced_index():
    """Проверка работы индекса связей: связанная группа -> True, свободный склад -> False."""
    # Arrange
    storage = storage_manager()
    service = reference_service(storage)
    grocery = next(g for g in storage.groups.values() if g.name == "Бакалея")
    free_wh = warehouse_model("Свободный склад", "ул. Свободная, 1")
    service.add(free_wh)

    # Act & Assert
    assert service.is_referenced(grocery) is True
    assert service.is_referenced(free_wh) is False


def test_success_reference_service_add_and_get():
    """Проверка создания новой сущности через сервис и поиска по ID."""
    # Arrange
    service = reference_service()
    new_wh = warehouse_model("Новый склад", "ул. Новая, 5")

    # Act
    added = service.add(new_wh)
    found = service.get_by_id(warehouse_model, new_wh.id)

    # Assert
    assert added is True
    assert found is not None
    assert found.name == "Новый склад"


def test_success_reference_service_delete_free_entity():
    """Проверка успешного удаления свободной сущности."""
    # Arrange
    service = reference_service()
    wh = warehouse_model("Временный склад", "ул. Мира, 10")
    service.add(wh)

    # Act
    deleted = service.delete(wh)

    # Assert
    assert deleted is True
    assert service.get_by_id(warehouse_model, wh.id) is None


def test_throw_exception_reference_service_delete_referenced_entity():
    """Проверка блокировки удаления связанной сущности."""
    # Arrange
    storage = storage_manager()
    service = reference_service(storage)
    grocery = next(g for g in storage.groups.values() if g.name == "Бакалея")

    # Act & Assert
    with pytest.raises(arguments_exception):
        service.delete(grocery)


def test_throw_exception_reference_service_update_referenced_id():
    """Проверка блокировки смены кода (ID) у связанной сущности."""
    # Arrange
    storage = storage_manager()
    service = reference_service(storage)
    grocery = next(g for g in storage.groups.values() if g.name == "Бакалея")
    new_group = group_model("Бакалея")  # новый UUID

    # Act & Assert
    with pytest.raises(arguments_exception):
        service.update(grocery.id, new_group)


def test_success_reference_service_update_free_entity_id():
    """Проверка возможности смены кода (ID) у свободной сущности."""
    # Arrange
    service = reference_service()
    free_group = group_model("Свободная группа")
    service.add(free_group)
    old_id = free_group.id

    updated_group = group_model("Обновленная группа")

    # Act
    result = service.update(old_id, updated_group)

    # Assert
    assert result is True
    assert service.get_by_id(group_model, old_id) is None
    assert service.get_by_id(group_model, updated_group.id) is not None

def test_throw_exception_reference_service_invalid_arguments():
    """Проверка валидации некорректных аргументов сервиса."""
    # Arrange
    service = reference_service()

    # Act & Assert
    with pytest.raises(arguments_exception):
        service.get_list(str)
    with pytest.raises(arguments_exception):
        service.add("не_модель")
    with pytest.raises(arguments_exception):
        service.is_referenced("не_модель")