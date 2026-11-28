import pytest

from main import app, init_app
from Src.Core.abstract_observer import abstract_observer
from Src.Core.event_type import event_type
from Src.Dtos.log_type_enum import log_type_enum
from Src.Logics.file_logger_observer import file_logger_observer
from Src.Logics.observe_service import observe_service
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Models.log_model import log_model
from Src.Models.transaction_model import transaction_model


class capturing_observer(abstract_observer):
    """Тестовый наблюдатель для проверки перехваченных событий."""

    def __init__(self):
        self.events = []

    def handler(self, event: event_type, params=None) -> None:
        self.events.append((event, params))


@pytest.fixture(autouse=True)
def setup_logging_env(tmp_path):
    """Готовит хранилище и подписывает тестовый и файловый наблюдатели."""
    saved_handlers = observe_service.handlers()
    observe_service.clear()
    storage_manager.clear()

    log_file = tmp_path / "integration.log"
    cap_obs = capturing_observer()
    observe_service.add(cap_obs)
    observe_service.add(file_logger_observer(str(log_file)))

    sm = settings_manager()
    sm.load()
    init_app()

    yield cap_obs, log_file

    observe_service.clear()
    storage_manager.clear()
    for h in saved_handlers:
        observe_service.add(h)


@pytest.fixture
def client():
    """Создает тестовый HTTP-клиент Connexion."""
    with app.test_client() as test_client:
        yield test_client


def test_success_logging_all_four_categories_and_file(client, setup_logging_env):
    """Проверка логирования CRUD, складских операций, Web-вызовов и изменения настроек."""
    cap_obs, log_file = setup_logging_env
    cap_obs.events.clear()

    # Web + CRUD
    create_resp = client.post(
        "/api/entity/warehouses",
        json={"name": "Склад логов", "address": "г. Москва, ул. Тестовая, 1"}
    )
    assert create_resp.status_code == 201
    wh_id = create_resp.json()["id"]
    assert client.delete(f"/api/entity/warehouses/{wh_id}").status_code == 200

    # Складская операция и ОСВ
    storage = storage_manager()
    wh = next(iter(storage.warehouses.values()))
    nom = next(iter(storage.nomenclature.values()))
    tx = transaction_model.create(wh, nom, nom.unit, 25.0)
    storage.add(tx)
    assert client.post("/api/reports/osv", json={}).status_code == 200

    # Изменение настроек
    fmt_resp = client.put("/api/settings/format", json={"response_format": "csv"})
    assert fmt_resp.status_code == 200
    settings_manager().set_response_format("markdown")

    # Проверяем получение логов через GET /api/logs
    logs_resp = client.get("/api/logs")
    assert logs_resp.status_code == 200

    events = {e[0] for e in cap_obs.events}
    assert event_type.CRUD_CREATE in events
    assert event_type.CRUD_DELETE in events
    assert event_type.STORAGE_OPERATION in events
    assert event_type.STORAGE_OSV in events
    assert event_type.WEB_REQUEST in events
    assert event_type.WEB_RESPONSE in events
    assert event_type.CHANGE_SETTINGS in events

    assert log_file.exists()
    content = log_file.read_text(encoding="utf-8")
    assert "CRUD" in content
    assert "Storage" in content
    assert "Web" in content
    assert "Settings" in content


def test_success_logging_crud_error_and_web_error(client, setup_logging_env):
    """Проверка записи ERROR при попытке удалить связанную сущность."""
    # Arrange
    cap_obs, _ = setup_logging_env
    cap_obs.events.clear()
    storage = storage_manager()
    grocery = next(g for g in storage.groups.values() if g.name == "Бакалея")

    # Act
    resp = client.delete(f"/api/entity/groups/{grocery.id}")

    # Assert
    assert resp.status_code == 400
    error_entries = [
        p for _, p in cap_obs.events
        if isinstance(p, log_model) and p.log_type == log_type_enum.ERROR
    ]
    assert len(error_entries) >= 2