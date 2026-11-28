import json
from Src.Core.abstract_manager import abstract_manager
from Src.Core.exception import arguments_exception
from Src.Models.settings_model import settings_model
from Src.Logics.deserialize_factory import deserialize_factory 
from Src.Core.event_type import event_type
from Src.Dtos.log_type_enum import log_type_enum
from Src.Dtos.report_type_enum import report_type_enum
from Src.Logics.observe_service import observe_service
from Src.Models.log_model import log_model

class settings_manager(abstract_manager):
    """
    Менеджер для работы с настройками приложения (Singleton).
    Загружает и конвертирует конфигурационный JSON-файл.
    """
    __default_file_name: str = "settings.json"
    __settings: settings_model = None
    __is_loaded: bool = False
    __data: dict = {}

    def __new__(cls):
        """Синглтон: гарантирует один экземпляр менеджера."""
        if not hasattr(cls, 'instance'):
            cls.instance = super(settings_manager, cls).__new__(cls)
        return cls.instance

    def load(self, file_name: str = "") -> bool:
        """
        Загрузка и обработка файла настроек.
        """
        if not isinstance(file_name, str):
            raise arguments_exception("Имя файла должно быть строкой")

        inner_file_name = file_name.strip() if file_name.strip() != "" else self.__default_file_name

        try:
            with open(inner_file_name, "r", encoding="utf-8") as file:
                self.__data = json.load(file)
                self.__is_loaded = self.convert()
                if self.__is_loaded:
                    observe_service.create(
                        event_type.LOAD_SETTINGS,
                        log_model.create("Settings", log_type_enum.INFO, f"Загружены настройки из файла '{inner_file_name}'", event_type.LOAD_SETTINGS)
                    )
                return self.__is_loaded
        except Exception:
            raise arguments_exception("Ошибка при загрузке и обработке файла")

    def convert(self) -> bool:
        """
        Обработка загруженных данных через общую фабрику десериализации.
        """
        if not self.__data or not isinstance(self.__data, dict):
            return False

        try:
            factory = deserialize_factory()
            self.__settings = factory.deserialize(self.__data, settings_model)
            return self.__settings is not None
        except Exception:
            return False

    @property
    def is_loaded(self) -> bool:
        """Флаг завершения загрузки и обработки данных."""
        return self.__is_loaded

    @property
    def settings(self) -> settings_model:
        """Полученный объект настроек."""
        return self.__settings

    def change_settings(self, new_settings: settings_model) -> None:
        """Обновляет объект настроек приложения."""
        if new_settings is None or not isinstance(new_settings, settings_model):
            raise arguments_exception("Настройки должны быть объектом settings_model", "new_settings")

        self.__settings = new_settings
        self.__is_loaded = True
        observe_service.create(
            event_type.CHANGE_SETTINGS,
            log_model.create("Settings", log_type_enum.INFO, "Изменены параметры настроек приложения", event_type.CHANGE_SETTINGS)
        )

    def set_response_format(self, response_format: report_type_enum | str) -> None:
        """Изменяет формат отчета по умолчанию в настройках и логирует событие."""
        if self.__settings is None:
            raise arguments_exception("Настройки не загружены", "settings")

        self.__settings.response_format = response_format
        observe_service.create(
            event_type.CHANGE_SETTINGS,
            log_model.create("Settings", log_type_enum.INFO, f"Изменен формат ответа по умолчанию на '{self.__settings.response_format.value}'", event_type.CHANGE_SETTINGS)
        )

