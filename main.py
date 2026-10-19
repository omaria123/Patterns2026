import connexion
from flask import Response

from Src.Dtos.report_type_enum import report_type_enum
from Src.Dtos.report_result_dto import report_result_dto
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Logics.report_factory import report_factory

app = connexion.FlaskApp(__name__, specification_dir="./")


def init_app():
    """Инициализация настроек и хранилища при старте сервера."""
    sm = settings_manager()
    if not sm.is_loaded:
        sm.load()

    storage = storage_manager()
    if not storage.is_loaded:
        storage.convert(sm.settings)


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


# Список объектов и их кодов (ID) 
@app.route("/api/list/<entity_type>", methods=["GET"])
def list_entities(entity_type: str):
    """Выводит список всех доступных сущностей с их кодами."""
    storage = storage_manager()
    items = storage.list_items(entity_type)
    if not items:
        return f"Сущности типа '{entity_type}' не найдены", 404

    lines = [f"Список сущностей типа '{entity_type}' (Код -> Наименование):"]
    for item in items:
        lines.append(f"{item.id} -> {item.name}")

    return Response("\n".join(lines), mimetype="text/plain; charset=utf-8")


# С явным указанием формата и кода сущности 
@app.route("/api/report/<format_type>/<entity_type>/<entity_id>", methods=["GET"])
def get_report_by_format(format_type: str, entity_type: str, entity_id: str):
    storage = storage_manager()

    # Поиск делегирован в storage_manager 
    entity = storage.get(entity_type, entity_id)
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

    factory = report_factory()
    report = factory.create(format_enum)
    result_dto = report.build(entity)
    return _format_http_response(result_dto)


# По умолчанию из настроек (create_default) по коду сущности
@app.route("/api/report/<entity_type>/<entity_id>", methods=["GET"])
def get_report_default(entity_type: str, entity_id: str):
    storage = storage_manager()

    # Поиск делегирован в storage_manager
    entity = storage.get(entity_type, entity_id)
    if not entity:
        return f"Сущность типа '{entity_type}' с кодом '{entity_id}' не найдена", 404

    factory = report_factory()
    report = factory.create_default()
    result_dto = report.build(entity)
    return _format_http_response(result_dto)


if __name__ == "__main__":
    storage = storage_manager()

    # Берем сгенерированные коды сущностей:
    r_id = list(storage.recipes.keys())[0] if storage.recipes else ""
    n_id = list(storage.nomenclature.keys())[0] if storage.nomenclature else ""
    u_id = list(storage.units.keys())[0] if storage.units else ""

    print("\n[INFO] Сервер запущен на http://localhost:8080")
    print("[INFO] Примеры рабочих запросов строго по коду (ID):")
    print("  1. Посмотреть коды номенклатуры:  http://localhost:8080/api/list/nomenclature")
    print("  2. Посмотреть коды рецептов:      http://localhost:8080/api/list/recipe")
    print(f"  3. Отчет XML по коду:             http://localhost:8080/api/report/xml/recipe/{r_id}")
    print(f"  4. Скачать CSV по коду:           http://localhost:8080/api/report/csv/recipe/{r_id}")
    print(f"  5. Отчет по умолчанию (п. 8):     http://localhost:8080/api/report/recipe/{r_id}\n")

    app.run(host="0.0.0.0", port=8080)