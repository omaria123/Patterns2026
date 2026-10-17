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


def _find_entity(entity_type: str, entity_id: str):
    """
    Поиск сущности в хранилище по типу и коду (ID).
    """
    storage = storage_manager()
    cleaned_type = entity_type.strip().lower()
    target_id = entity_id.strip()

    collection = {}
    if cleaned_type in ("recipe", "рецепт"):
        collection = storage.recipes
    elif cleaned_type in ("nomenclature", "номенклатура"):
        collection = storage.nomenclature
    elif cleaned_type in ("unit", "единица", "range"):
        collection = storage.units
    else:
        return None, f"Неизвестный тип сущности: '{entity_type}'. Допустимые: recipe, nomenclature, unit"

    # Ищем по совпадению ID 
    for item_id, item in collection.items():
        if str(item_id) == target_id:
            return item, None

    return None, f"Сущность типа '{entity_type}' с кодом '{entity_id}' не найдена"


def _format_http_response(result_dto: report_result_dto, format_enum: report_type_enum, filename_base: str):
    """Формирование HTTP-ответа (Пункт 7 ТЗ: скачивание для CSV/Markdown, текст для остальных)."""
    if format_enum == report_type_enum.CSV:
        return Response(
            bytes(result_dto.binary),
            mimetype="text/csv; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename={filename_base}.csv"}
        )

    if format_enum == report_type_enum.MARKDOWN:
        return Response(
            bytes(result_dto.binary),
            mimetype="text/markdown; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename={filename_base}.md"}
        )

    if format_enum == report_type_enum.XML:
        return Response(result_dto.text, mimetype="application/xml; charset=utf-8")

    if format_enum == report_type_enum.HTML:
        return Response(result_dto.text, mimetype="text/html; charset=utf-8")

    return Response(result_dto.text, mimetype="text/plain; charset=utf-8")


# Список объектов и их кодов (ID) 
@app.route("/api/list/<entity_type>", methods=["GET"])
def list_entities(entity_type: str):
    """Выводит список всех доступных сущностей с их кодами."""
    storage = storage_manager()
    cleaned_type = entity_type.strip().lower()

    collection = {}
    if cleaned_type in ("recipe", "рецепт"):
        collection = storage.recipes
    elif cleaned_type in ("nomenclature", "номенклатура"):
        collection = storage.nomenclature
    elif cleaned_type in ("unit", "единица", "range"):
        collection = storage.units
    else:
        return f"Неизвестный тип: {entity_type}", 400

    lines = [f"Список сущностей типа '{entity_type}' (Код -> Наименование):"]
    for item_id, item in collection.items():
        lines.append(f"{item_id} -> {item.name}")

    return Response("\n".join(lines), mimetype="text/plain; charset=utf-8")


# С явным указанием формата и кода сущности 
@app.route("/api/report/<format_type>/<entity_type>/<entity_id>", methods=["GET"])
def get_report_by_format(format_type: str, entity_type: str, entity_id: str):
    entity, error = _find_entity(entity_type, entity_id)
    if error:
        return error, 404

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
    return _format_http_response(result_dto, format_enum, f"report_{entity_type}")


# По умолчанию из настроек (create_default) по коду сущности
@app.route("/api/report/<entity_type>/<entity_id>", methods=["GET"])
def get_report_default(entity_type: str, entity_id: str):
    entity, error = _find_entity(entity_type, entity_id)
    if error:
        return error, 404

    factory = report_factory()
    report = factory.create_default()
    result_dto = report.build(entity)
    default_format = getattr(factory.settings, "response_format", report_type_enum.MARKDOWN)

    return _format_http_response(result_dto, default_format, f"report_default_{entity_type}")


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