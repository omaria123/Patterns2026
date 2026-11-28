from enum import StrEnum


class event_type(StrEnum):
    """Перечисление типов системных событий для шаблона Наблюдатель."""

    # Настройки
    LOAD_SETTINGS = "load_settings"
    CHANGE_SETTINGS = "change_settings"

    # CRUD операции
    CRUD_CREATE = "crud_create"
    CRUD_READ = "crud_read"
    CRUD_UPDATE = "crud_update"
    CRUD_DELETE = "crud_delete"
    CRUD_ERROR = "crud_error"

    # Складские операции
    STORAGE_LOAD = "storage_load"
    STORAGE_OPERATION = "storage_operation"
    STORAGE_OSV = "storage_osv"

    # Вызовы Web-методов
    WEB_REQUEST = "web_request"
    WEB_RESPONSE = "web_response"