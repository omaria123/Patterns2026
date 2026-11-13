import json
from flask import Response, request

from Src.Core.exception import arguments_exception
from Src.Logics.convert_factory import convert_factory
from Src.Logics.deserialize_factory import deserialize_factory
from Src.Logics.storage_manager import storage_manager


def _json_response(payload, status: int = 200) -> Response:
    """Формирование HTTP-ответа в формате JSON."""
    return Response(
        json.dumps(payload, ensure_ascii=False),
        status=status,
        mimetype="application/json; charset=utf-8"
    )


def get_entity(entity_type: str, entity_id: str):
    """Получение доменной сущности в формате JSON по типу и уникальному коду."""
    storage = storage_manager()
    if storage.get_model_class(entity_type) is None:
        return _json_response({"error": f"Неизвестный тип сущности '{entity_type}'"}, status=404)

    entity = storage.get(entity_type, entity_id)
    if entity is None:
        return _json_response({"error": f"Сущность '{entity_type}' с кодом '{entity_id}' не найдена"}, status=404)

    return _json_response(convert_factory().convert(entity), status=200)


def create_entity(entity_type: str, body: dict = None):
    """Создание и сохранение новой доменной сущности из JSON-запроса."""
    storage = storage_manager()
    expected_cls = storage.get_model_class(entity_type)
    if expected_cls is None:
        return _json_response({"error": f"Неизвестный тип сущности '{entity_type}'"}, status=404)

    data = body if body is not None else request.get_json(silent=True)
    if not isinstance(data, dict):
        return _json_response({"error": "Тело запроса должно быть JSON-объектом"}, status=400)

    try:
        # Восстанавливаем модель из JSON и проверяем совпадение типа
        entity = deserialize_factory().deserialize(data, target_type=expected_cls)
        if not isinstance(entity, expected_cls):
            raise arguments_exception(f"Сущность не соответствует типу '{entity_type}'", "type")

        if not storage.add(entity):
            return _json_response({"error": f"Сущность с кодом '{entity.id}' уже существует"}, status=400)

        return _json_response(convert_factory().convert(entity), status=201)
    except (arguments_exception, ValueError) as exc:
        return _json_response({"error": str(exc)}, status=400)


def update_entity(entity_type: str, entity_id: str, body: dict = None):
    """Обновление существующей доменной сущности по типу и коду."""
    storage = storage_manager()
    expected_cls = storage.get_model_class(entity_type)
    if expected_cls is None:
        return _json_response({"error": f"Неизвестный тип сущности '{entity_type}'"}, status=404)

    existing = storage.get(entity_type, entity_id)
    if existing is None:
        return _json_response({"error": f"Сущность '{entity_type}' с кодом '{entity_id}' не найдена"}, status=404)

    data = body if body is not None else request.get_json(silent=True)
    if not isinstance(data, dict):
        return _json_response({"error": "Тело запроса должно быть JSON-объектом"}, status=400)

    # Если код не передан в теле запроса, сохраняем исходный код сущности
    payload = dict(data)
    if "id" not in payload or not payload["id"]:
        payload["id"] = str(existing.id)

    try:
        new_item = deserialize_factory().deserialize(payload, target_type=expected_cls)
        if not isinstance(new_item, expected_cls):
            raise arguments_exception(f"Сущность не соответствует типу '{entity_type}'", "type")

        storage.update(entity_type, entity_id, new_item)
        return _json_response(convert_factory().convert(new_item), status=200)
    except (arguments_exception, ValueError) as exc:
        return _json_response({"error": str(exc)}, status=400)


def delete_entity(entity_type: str, entity_id: str):
    """Удаление доменной сущности с проверкой отсутствия связей."""
    storage = storage_manager()
    if storage.get_model_class(entity_type) is None:
        return _json_response({"error": f"Неизвестный тип сущности '{entity_type}'"}, status=404)

    try:
        deleted = storage.delete(entity_type, entity_id)
        if not deleted:
            return _json_response({"error": f"Сущность '{entity_type}' с кодом '{entity_id}' не найдена"}, status=404)

        return _json_response({"status": "deleted", "id": str(entity_id)}, status=200)
    except (arguments_exception, ValueError) as exc:
        return _json_response({"error": str(exc)}, status=400)