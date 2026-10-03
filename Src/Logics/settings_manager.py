import json
from Src.Core.abstract_manager import abstract_manager
from Src.Core.exception import arguments_exception
from Src.Models.settings_model import settings_model
from Src.Models.organization_model import organization_model


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
        Обработка загруженных данных и наполнение модели settings_model.
        """
        if not self.__data or not isinstance(self.__data, dict):
            return False

        try:
            settings = settings_model()
            settings.boss_name = self.__data.get("boss_name", "")
            settings.account_name = self.__data.get("account_name", "")

            if "is_first_start" in self.__data:
                settings.is_first_start = bool(self.__data["is_first_start"])

            # Заполняем организацию
            org_data = self.__data.get("organization", {})
            if isinstance(org_data, dict):
                org = organization_model(
                    name=org_data.get("name", ""),
                    inn=org_data.get("inn", ""),
                    bik=org_data.get("bik", ""),
                    account=org_data.get("account", ""),
                    ownership_form=org_data.get("ownership_form", "")
                )
                settings.organization = org

            self.__settings = settings
            return True
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