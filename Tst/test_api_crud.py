from uuid import uuid4
import pytest

from main import app, init_app
from Src.Logics.convert_factory import convert_factory
from Src.Logics.storage_manager import storage_manager


@pytest.fixture(autouse=True)
def setup_storage():
    """Инициализация чистого хранилища перед каждым интеграционным тестом."""
    storage_manager.clear()
    init_app()
    yield
    storage_manager.clear()


@pytest.fixture
def client():
    """Создание тестового HTTP-клиента Connexion."""
    with app.test_client() as test_client:
        yield test_client


def test_success_api_get_report_formats(client):
    """Проверка получения списка всех поддерживаемых форматов отчетов."""
    # Act
    response = client.get("/api/reports/formats")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert set(data) == {"txt", "csv", "markdown", "xml", "html"}


def test_success_api_crud_warehouse_lifecycle(client):
    """Проверка полного цикла CRUD для свободной сущности."""
    # Arrange
    create_payload = {
        "name": "Склад ресторана №2",
        "address": "г. Москва, ул. Тверская, д. 15"
    }

    # Act 1: Создание (POST)
    create_resp = client.post("/api/entity/warehouse", json=create_payload)
    assert create_resp.status_code == 201
    created = create_resp.json()
    wh_id = created["id"]
    assert created["name"] == "Склад ресторана №2"

    # Act 2: Чтение (GET)
    get_resp = client.get(f"/api/entity/warehouse/{wh_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == wh_id

    # Act 3: Обновление (PUT)
    update_payload = {
        "id": wh_id,
        "name": "Склад №2 обновленный",
        "address": "г. Москва, ул. Тверская, д. 20"
    }
    update_resp = client.put(f"/api/entity/warehouse/{wh_id}", json=update_payload)
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "Склад №2 обновленный"

    # Act 4: Удаление свободной сущности 
    delete_resp = client.delete(f"/api/entity/warehouse/{wh_id}")
    assert delete_resp.status_code == 200

    # Assert: После удаления сущность больше не найдена
    assert client.get(f"/api/entity/warehouse/{wh_id}").status_code == 404


def test_success_api_create_nomenclature_with_relations(client):
    """Проверка создания номенклатуры со ссылками на группу и единицу измерения."""
    # Arrange
    storage = storage_manager()
    c_factory = convert_factory()
    group = next(iter(storage.groups.values()))
    unit = next(iter(storage.units.values()))

    payload = {
        "name": "Сахар",
        "full_name": "Сахар белый кристаллический",
        "group": c_factory.convert(group),
        "unit": c_factory.convert(unit)
    }

    # Act
    response = client.post("/api/entity/nomenclature", json=payload)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Сахар"
    assert data["group"]["id"] == str(group.id)


def test_throw_api_create_invalid_data(client):
    """Проверка валидации при создании сущностей с некорректными данными."""
    # Arrange
    storage = storage_manager()
    existing_group = next(iter(storage.groups.values()))

    # Act & Assert: пустое наименование
    assert client.post("/api/entity/group", json={"name": "   "}).status_code == 400

    # Act & Assert: неизвестный тип сущности
    assert client.post("/api/entity/unknown_type", json={"name": "Тест"}).status_code == 404

    # Act & Assert: дубликат существующего кода (ID)
    dup_payload = {"id": str(existing_group.id), "name": "Дубликат"}
    assert client.post("/api/entity/group", json=dup_payload).status_code == 400


def test_throw_api_delete_referenced_group_blocked(client):
    """Проверка запрета удаления группы номенклатуры, связанной с товарами."""
    # Arrange
    storage = storage_manager()
    grocery = next(g for g in storage.groups.values() if g.name == "Бакалея")

    # Act
    response = client.delete(f"/api/entity/group/{grocery.id}")

    # Assert
    assert response.status_code == 400
    assert client.get(f"/api/entity/group/{grocery.id}").status_code == 200


def test_throw_api_delete_referenced_unit_blocked(client):
    """Проверка запрета удаления единицы измерения, связанной с другими данными."""
    # Arrange
    storage = storage_manager()
    gram = next(u for u in storage.units.values() if u.name == "грамм")

    # Act
    response = client.delete(f"/api/entity/unit/{gram.id}")

    # Assert
    assert response.status_code == 400
    assert client.get(f"/api/entity/unit/{gram.id}").status_code == 200


def test_throw_api_delete_referenced_nomenclature_blocked(client):
    """Проверка запрета удаления номенклатуры, используемой в рецепте."""
    # Arrange
    storage = storage_manager()
    flour = next(n for n in storage.nomenclature.values() if n.name == "Мука пшеничная")

    # Act
    response = client.delete(f"/api/entity/nomenclature/{flour.id}")

    # Assert
    assert response.status_code == 400
    assert client.get(f"/api/entity/nomenclature/{flour.id}").status_code == 200


def test_throw_api_update_change_id_of_referenced_entity_blocked(client):
    """Проверка запрета смены кода (ID) у связанной сущности."""
    # Arrange
    storage = storage_manager()
    grocery = next(g for g in storage.groups.values() if g.name == "Бакалея")
    new_id = str(uuid4())

    # Act
    response = client.put(
        f"/api/entity/group/{grocery.id}",
        json={"id": new_id, "name": "Бакалея"}
    )

    # Assert
    assert response.status_code == 400
    assert client.get(f"/api/entity/group/{grocery.id}").status_code == 200
    assert client.get(f"/api/entity/group/{new_id}").status_code == 404


def test_success_api_update_referenced_entity_without_changing_id(client):
    """Проверка возможности обновления связанной сущности"""
    # Arrange
    storage = storage_manager()
    grocery = next(g for g in storage.groups.values() if g.name == "Бакалея")

    # Act
    response = client.put(
        f"/api/entity/group/{grocery.id}",
        json={"id": str(grocery.id), "name": "Бакалея Премиум"}
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["name"] == "Бакалея Премиум"