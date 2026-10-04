import pytest
from Src.Logics.settings_manager import settings_manager
from Src.Models.settings_model import settings_model
from Src.Core.exception import arguments_exception


def test_not_raise_settings_manager_load():
    """Проверка, что вызов load() со стандартным файлом не вызывает исключений."""
    # Arrange
    manager = settings_manager()

    # Act & Assert
    try:
        manager.load()
        assert True
    except arguments_exception:
        assert False
    except Exception:
        assert False


def test_not_empty_settings_manager_load():
    """Проверка, что объект settings формируется после загрузки."""
    # Arrange
    manager = settings_manager()

    # Act
    try:
        manager.load()
    except Exception:
        assert False

    # Assert
    assert manager.settings is not None


def test_equals_settings_manager_create():
    """Проверка равенства двух экземпляров менеджера."""
    # Arrange & Act
    instance1 = settings_manager()
    instance2 = settings_manager()

    # Assert
    assert instance1 == instance2


def test_is_loaded_settings_manager_true():
    """Проверка, что флаг is_loaded становится True после успешной загрузки."""
    # Arrange
    manager = settings_manager()

    # Act
    try:
        manager.load()
    except Exception:
        assert False

    # Assert
    assert manager.is_loaded is True


def test_success_settings_manager_is_singleton():
    """Проверка работы паттерна Синглтон (один и тот же объект в памяти)."""
    # Arrange & Act
    manager1 = settings_manager()
    manager2 = settings_manager()

    # Assert
    assert manager1 == manager2
    assert manager1 is manager2


def test_success_settings_manager_convert_data_correctly():
    """Проверка корректности работы метода convert(): поля модели должны совпадать с JSON."""
    # Arrange
    manager = settings_manager()

    # Act
    manager.load()

    # Assert: проверяем директора и счет
    assert manager.settings.boss_name == "Иванов Иван Иванович"
    assert manager.settings.account_name == "Основной расчетный счет"

    # Assert: проверяем вложенную организацию
    assert manager.settings.organization.name == "ООО Ромашка"
    assert manager.settings.organization.inn == "1234567890"
    assert manager.settings.organization.bik == "044525225"
    assert manager.settings.organization.account == "40702810400000001234"
    assert manager.settings.organization.ownership_form == "ООО"


def test_throw_exception_settings_manager_file_not_found():
    """Проверка выброса исключения arguments_exception при попытке загрузить несуществующий файл."""
    # Arrange
    manager = settings_manager()
    invalid_filename = "file_does_not_exist_123.json"

    # Act & Assert
    with pytest.raises(arguments_exception):
        manager.load(invalid_filename)


def test_throw_exception_settings_manager_invalid_filename_type():
    """Проверка валидации: передача числа вместо имени файла вызывает arguments_exception."""
    # Arrange
    manager = settings_manager()
    invalid_type_name = 12345

    # Act & Assert
    with pytest.raises(arguments_exception):
        manager.load(invalid_type_name)