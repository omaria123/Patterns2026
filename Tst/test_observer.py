import pytest

from Src.Core.abstract_observer import abstract_observer
from Src.Core.event_type import event_type
from Src.Core.exception import arguments_exception
from Src.Dtos.log_type_enum import log_type_enum
from Src.Logics.file_logger_observer import file_logger_observer
from Src.Logics.observe_service import observe_service
from Src.Models.group_model import group_model
from Src.Models.log_model import log_model


class capturing_observer(abstract_observer):
    """Тестовый наблюдатель для перехвата событий."""

    def __init__(self):
        self.events = []

    def handler(self, event: event_type, params=None) -> None:
        self.events.append((event, params))


@pytest.fixture(autouse=True)
def restore_observers():
    """Сохраняет и восстанавливает список наблюдателей после каждого теста."""
    saved_handlers = observe_service.handlers()
    observe_service.clear()
    yield
    observe_service.clear()
    for h in saved_handlers:
        observe_service.add(h)


def test_success_observer_notifies_handlers_and_file(tmp_path):
    """Проверка уведомления наблюдателей и записи в файл."""
    # Arrange
    log_file = tmp_path / "test.log"
    cap_obs = capturing_observer()
    file_obs = file_logger_observer(str(log_file))

    observe_service.add(cap_obs)
    observe_service.add(file_obs)
    observe_service.add(file_obs)

    entry = log_model.create("CRUD", log_type_enum.INFO, "Создана группа", event_type.CRUD_CREATE)

    # Act
    observe_service.create(event_type.CRUD_CREATE, entry)

    # Assert
    assert len(observe_service.handlers()) == 2
    assert len(cap_obs.events) == 1
    assert log_file.exists()
    content = log_file.read_text(encoding="utf-8")
    assert "INFO" in content
    assert "Создана группа" in content


def test_success_observer_delete_unsubscribes_handler():
    """Проверка отписки наблюдателя и работы события с обычной моделью."""
    # Arrange
    cap_obs = capturing_observer()
    observe_service.add(cap_obs)
    group = group_model("Бакалея")

    # Act
    observe_service.create(event_type.CRUD_READ, group)
    observe_service.delete(cap_obs)
    observe_service.create(event_type.CRUD_READ, group)

    # Assert
    assert len(cap_obs.events) == 1


def test_throw_exception_observer_invalid_arguments():
    """Проверка валидации неверных аргументов в observe_service и file_logger_observer."""
    # Act & Assert
    with pytest.raises(arguments_exception):
        observe_service.add("не_наблюдатель")

    with pytest.raises(arguments_exception):
        observe_service.create("неизвестное_событие")

    with pytest.raises(arguments_exception):
        observe_service.create(event_type.LOAD_SETTINGS, "строка")

    with pytest.raises(arguments_exception):
        file_logger_observer("   ")