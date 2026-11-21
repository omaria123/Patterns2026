import pytest

from main import app, init_app
from Src.Logics.storage_manager import storage_manager


@pytest.fixture(autouse=True)
def setup_storage():
    """Инициализация хранилища перед каждым интеграционным тестом."""
    storage_manager.clear()
    init_app()
    yield
    storage_manager.clear()


@pytest.fixture
def client():
    """Создание тестового HTTP-клиента Connexion."""
    with app.test_client() as test_client:
        yield test_client


def test_success_api_filter_nomenclature_like(client):
    """Проверка фильтрации номенклатуры через POST /api/filter/{entity_type}."""
    # Act
    response = client.post(
        "/api/filter/nomenclature",
        json={"name": "мука", "filter_type": "like"}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Мука пшеничная"


def test_success_api_filter_units_nested_base_unit(client):
    """Проверка вложенного поиска единиц измерения по базовой единице через API."""
    # Act
    response = client.post(
        "/api/filter/units",
        json={"nested": {"name": "грамм", "filter_type": "equals"}}
    )

    # Assert
    assert response.status_code == 200
    names = {item["name"] for item in response.json()}
    assert names == {"грамм", "килограмм"}


def test_success_api_filter_groups_by_unique_code(client):
    """Проверка фильтрации групп по уникальному коду через API."""
    # Arrange
    storage = storage_manager()
    grocery = next(g for g in storage.groups.values() if g.name == "Бакалея")

    # Act
    response = client.post(
        "/api/filter/groups",
        json={"unique_code": str(grocery.id), "filter_type": "equals"}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Бакалея"


def test_throw_api_filter_invalid_params(client):
    """Проверка возврата 400 при некорректном типе фильтрации или неизвестной модели."""
    # Act & Assert: некорректный режим фильтрации
    resp_mode = client.post(
        "/api/filter/nomenclature",
        json={"name": "Мука", "filter_type": "unknown_mode"}
    )
    assert resp_mode.status_code == 400

    # Act & Assert: неизвестная модель
    resp_entity = client.post(
        "/api/filter/unknown_entity",
        json={"name": "Тест"}
    )
    assert resp_entity.status_code == 400


def test_success_api_osv_all_and_filtered_by_period(client):
    """Проверка формирования ОСВ через POST /api/reports/osv с учетом фильтрации и периода."""
    # Act 1: Полная ОСВ
    full_resp = client.post("/api/reports/osv", json={})
    assert full_resp.status_code == 200
    assert len(full_resp.json()) == 4

    # Act 2: ОСВ по муке за период (с начальным остатком)
    filtered_resp = client.post(
        "/api/reports/osv",
        json={
            "name": "мука",
            "filter_type": "like",
            "start_period": "2026-11-08T00:00:00",
            "end_period": "2026-11-20T23:59:59"
        }
    )

    # Assert
    assert filtered_resp.status_code == 200
    rows = filtered_resp.json()
    main_row = next(r for r in rows if r["warehouse"]["name"] == "Центральный склад цеха")
    assert main_row["opening_balance"] == 50.0
    assert main_row["income"] == 0.0
    assert main_row["outcome"] == 12.0
    assert main_row["closing_balance"] == 38.0


def test_throw_api_osv_invalid_date(client):
    """Проверка ошибки 400 при передаче некорректной даты в фильтр ОСВ."""
    # Act
    response = client.post("/api/reports/osv", json={"start_period": "не-дата"})

    # Assert
    assert response.status_code == 400