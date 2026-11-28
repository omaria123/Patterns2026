import connexion
from flask import Response, request
import json
from uuid import UUID

from Src.Dtos.filter_dto import filter_dto
from Src.Logics.prototype import prototype
from Src.Logics.turnover_service import turnover_service
from Src.Dtos.report_type_enum import report_type_enum
from Src.Dtos.report_result_dto import report_result_dto
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Logics.report_factory import report_factory
from Src.Core.exception import arguments_exception
from Src.Logics.convert_factory import convert_factory
from Src.Logics.reference_service import reference_service
from Src.Logics.deserialize_factory import deserialize_factory
from Src.Core.event_type import event_type
from Src.Dtos.log_type_enum import log_type_enum
from Src.Logics.observe_service import observe_service
from Src.Models.log_model import log_model
from Src.Logics.file_logger_observer import file_logger_observer

app = connexion.FlaskApp(__name__, specification_dir="./")
service: reference_service | None = None
osv_service: turnover_service | None = None

def init_app():
    """Инициализация настроек и хранилища при старте сервера."""
    global service, osv_service
    observe_service.add(file_logger_observer("logs.log"))
    sm = settings_manager()
    if not sm.is_loaded:
        sm.load()

    storage = storage_manager()
    if not storage.is_loaded:
        storage.convert(sm.settings)
    service = reference_service(storage)
    osv_service = turnover_service(storage)

init_app()


def _format_http_response(result_dto: report_result_dto):
    """
    Формирование HTTP-ответа (скачивание для CSV/Markdown, текст для остальных).
    Метаданные инкапсулированы в DTO.
    """
    headers = {}
    if result_dto.as_attachment:
        headers["Content-Disposition"] = f"attachment; filename={result_dto.file_name}"

    return Response(result_dto.data, mimetype=result_dto.mimetype, headers=headers)

def _json_response(payload, status: int = 200, mimetype: str = "application/json; charset=utf-8") -> Response:
    """Формирование JSON-ответа через convert_factory."""
    serialized = service.serialize(payload)
    return Response(
        json.dumps(serialized, ensure_ascii=False),
        status=status,
        mimetype=mimetype
    )

def _parse_uuid(raw_id: str) -> UUID:
    """Преобразует строковый идентификатор из URL в объект UUID."""
    try:
        return UUID(str(raw_id).strip())
    except ValueError:
        raise arguments_exception(f"Некорректный формат кода (UUID): '{raw_id}'", "entity_id")

@app.app.before_request
def _log_web_request():
    """Логирование входящего HTTP-запроса."""
    observe_service.create(
        event_type.WEB_REQUEST,
        log_model.create("Web", log_type_enum.DEBUG, f"Запрос: {request.method} {request.path}", event_type.WEB_REQUEST)
    )

@app.app.after_request
def _log_web_response(response):
    """Логирование результата HTTP-ответа."""
    level = log_type_enum.INFO if response.status_code < 400 else log_type_enum.ERROR
    observe_service.create(
        event_type.WEB_RESPONSE,
        log_model.create("Web", level, f"Ответ: {request.method} {request.path} -> {response.status_code}", event_type.WEB_RESPONSE)
    )
    return response
# Список объектов и их кодов (ID) 
@app.route("/api/list/<entity_type>", methods=["GET"])
def list_entities(entity_type: str):
    """Выводит список всех доступных сущностей с их кодами."""
    try:
        target_cls = service.resolve_model_type(entity_type)
        items = service.get_list(target_cls)
    except arguments_exception:
        return f"Сущности типа '{entity_type}' не найдены", 404

    if not items:
        return f"Сущности типа '{entity_type}' не найдены", 404

    lines = [f"Список сущностей типа '{entity_type}' (Код -> Наименование):"]
    for item in items:
        lines.append(f"{item.id} -> {item.name}")

    return Response("\n".join(lines), mimetype="text/plain; charset=utf-8")

@app.route("/api/report/<format_type>/<entity_type>/<entity_id>", methods=["GET"])
def get_report_by_format(format_type: str, entity_type: str, entity_id: str):
    """Формирует отчет по указанному формату и коду сущности."""
    try:
        target_cls = service.resolve_model_type(entity_type)
        uid = _parse_uuid(entity_id)
        entity = service.get_by_id(target_cls, uid)
    except arguments_exception as exc:
        return str(exc), 400

    if not entity:
        return f"Сущность типа '{entity_type}' с кодом '{entity_id}' не найдена", 404

    format_enum = None
    cleaned_format = format_type.strip().lower()
    for item in report_type_enum:
        if str(item.value).lower() == cleaned_format or item.name.lower() == cleaned_format:
            format_enum = item
            break
    if format_enum is None:
        return f"Неподдерживаемый формат: '{format_type}'", 400

    report = report_factory().create(format_enum)
    return _format_http_response(report.build(entity))

# По умолчанию из настроек (create_default) по коду сущности
@app.route("/api/report/<entity_type>/<entity_id>", methods=["GET"])
def get_report_default(entity_type: str, entity_id: str):
    """Формирует отчет в формате по умолчанию из настроек."""
    try:
        target_cls = service.resolve_model_type(entity_type)
        uid = _parse_uuid(entity_id)
        entity = service.get_by_id(target_cls, uid)
    except arguments_exception as exc:
        return str(exc), 400

    if not entity:
        return f"Сущность типа '{entity_type}' с кодом '{entity_id}' не найдена", 404

    report = report_factory().create_default()
    return _format_http_response(report.build(entity))


# Подключение Swagger 
def get_entities():
    """Возвращает список ключей доменных сущностей через общий сериализатор."""
    return _json_response(service.get_domains(), status=200, mimetype="text/json")


def get_default_report(entity: str, unique_code: str):
    """Формирует отчет по умолчанию через OpenAPI."""
    return get_report_default(entity, unique_code)


def get_report_formats():
    """Возвращает список форматов отчетов через общий сериализатор."""
    formats = [item.value for item in report_type_enum]
    return _json_response(formats, status=200)


def get_entity(entity_type: str, entity_id: str):
    """Возвращает доменную сущность по типу и коду."""
    try:
        target_cls = service.resolve_model_type(entity_type)
        uid = _parse_uuid(entity_id)
        entity = service.get_by_id(target_cls, uid)
        if entity is None:
            return _json_response({"error": f"Сущность '{entity_type}' с кодом '{entity_id}' не найдена"}, status=404)
        return _json_response(entity, status=200)
    except arguments_exception as exc:
        return _json_response({"error": str(exc)}, status=400)

def create_entity(entity_type: str, body: dict = None):
    """Десериализует входящий JSON и сохраняет модель через сервисный слой."""
    data = body if body is not None else request.get_json(silent=True)
    if not isinstance(data, dict) or not data:
        return _json_response({"error": "Тело запроса должно быть непустым JSON-объектом"}, status=400)

    try:
        target_cls = service.resolve_model_type(entity_type)
        entity = deserialize_factory().deserialize(data, target_type=target_cls)
        if type(entity) is not target_cls:
            raise arguments_exception(f"Сущность не соответствует типу '{entity_type}'", "type")

        if not service.add(entity):
            return _json_response({"error": f"Сущность с кодом '{entity.id}' уже существует"}, status=400)

        return _json_response(entity, status=201)
    except (arguments_exception, ValueError) as exc:
        return _json_response({"error": str(exc)}, status=400)

def update_entity(entity_type: str, entity_id: str, body: dict = None):
    """Десериализует входящий JSON и обновляет модель через сервисный слой."""
    data = body if body is not None else request.get_json(silent=True)
    if not isinstance(data, dict) or not data:
        return _json_response({"error": "Тело запроса должно быть непустым JSON-объектом"}, status=400)

    try:
        target_cls = service.resolve_model_type(entity_type)
        uid = _parse_uuid(entity_id)
        existing = service.get_by_id(target_cls, uid)
        if existing is None:
            return _json_response({"error": f"Сущность '{entity_type}' с кодом '{entity_id}' не найдена"}, status=404)

        payload = dict(data)
        if "id" not in payload or not payload["id"]:
            payload["id"] = str(existing.id)

        new_item = deserialize_factory().deserialize(payload, target_type=target_cls)
        if type(new_item) is not target_cls:
            raise arguments_exception(f"Сущность не соответствует типу '{entity_type}'", "type")

        service.update(uid, new_item)
        return _json_response(new_item, status=200)
    except (arguments_exception, ValueError) as exc:
        return _json_response({"error": str(exc)}, status=400)



def delete_entity(entity_type: str, entity_id: str):
    """Удаляет доменную сущность через сервисный слой."""
    try:
        target_cls = service.resolve_model_type(entity_type)
        uid = _parse_uuid(entity_id)
        existing = service.get_by_id(target_cls, uid)
        if existing is None:
            return _json_response({"error": f"Сущность '{entity_type}' с кодом '{entity_id}' не найдена"}, status=404)

        service.delete(existing)
        return _json_response({"status": "deleted", "id": str(uid)}, status=200)
    except (arguments_exception, ValueError) as exc:
        return _json_response({"error": str(exc)}, status=400)

def filter_entities(entity_type: str, body: dict = None):
    """POST /api/filter/{entity_type} — фильтрует доменные модели через шаблон Прототип."""
    data = body if body is not None else request.get_json(silent=True)
    if not isinstance(data, dict):
        return _json_response({"error": "Тело запроса должно быть JSON-объектом"}, status=400)

    try:
        target_cls = service.resolve_model_type(entity_type)
        filter_model = deserialize_factory().deserialize(data, target_type=filter_dto)
        items = service.get_list(target_cls)
        filtered = prototype(items).clone(filter_model).data
        return _json_response(filtered, status=200)
    except (arguments_exception, ValueError) as exc:
        return _json_response({"error": str(exc)}, status=400)


def get_osv_report(body: dict = None):
    """POST /api/reports/osv — формирует ОСВ с учетом фильтрации через Прототип."""
    data = body if body is not None else request.get_json(silent=True)
    if not isinstance(data, dict):
        return _json_response({"error": "Тело запроса должно быть JSON-объектом"}, status=400)

    try:
        filter_model = deserialize_factory().deserialize(data, target_type=filter_dto)
        rows = osv_service.build(filter_model)
        return _json_response(rows, status=200)
    except (arguments_exception, ValueError) as exc:
        return _json_response({"error": str(exc)}, status=400)

def get_logs():
    """Возвращает записи журнала из файла лога."""
    return _json_response(file_logger_observer("logs.log").read_logs(), status=200)

def change_settings_format(body: dict = None):
    """Изменяет формат отчета по умолчанию в настройках и логирует событие."""
    data = body if body is not None else request.get_json(silent=True)
    if not isinstance(data, dict) or "response_format" not in data:
        return _json_response({"error": "Необходимо передать поле response_format"}, status=400)
    try:
        settings_manager().set_response_format(data["response_format"])
        return _json_response({"response_format": settings_manager().settings.response_format.value}, status=200)
    except arguments_exception as exc:
        return _json_response({"error": str(exc)}, status=400)

app.add_api("openapi.yml")

if __name__ == "__main__":
    print("\n[INFO] Сервер запущен на http://localhost:8080")
    print("[INFO] Swagger UI: http://localhost:8080/ui/\n")
    app.run(host="0.0.0.0", port=8080)