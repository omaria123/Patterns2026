import json
from Src.Core.abstract_manager import abstract_manager
from Src.Core.exception import arguments_exception
from Src.Models.settings_model import settings_model
from Src.Logics.deserialize_factory import deserialize_factory 

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