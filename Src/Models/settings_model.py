from Src.Core.abstract_class import abstract_reference
from Src.Models.organization_model import organization_model
from Src.Core.exception import arguments_exception


class settings_model(abstract_reference):
    """
    Модель настроек приложения.
    Хранит информацию о директоре, счете и организации.
    """
    __organization: organization_model = None
    __boss_name: str = ""
    __account_name: str = ""
    __is_first_start: bool = True

    @property
    def organization(self) -> organization_model:
        """Геттер объекта организации."""
        return self.__organization

    @organization.setter
    def organization(self, value: organization_model) -> None:
        """Сеттер объекта организации с проверкой типа."""
        if not isinstance(value, organization_model):
            raise arguments_exception("Организация должна быть типа organization_model")
        self.__organization = value

    @property
    def boss_name(self) -> str:
        """Геттер имени руководителя."""
        return self.__boss_name

    @boss_name.setter
    def boss_name(self, value: str):
        """Сеттер имени руководителя."""
        self._validation_boss(value)
        self.__boss_name = value.strip()

    def _validation_boss(self, value):
        """Проверка, что имя руководителя — непустая строка."""
        if not isinstance(value, str) or not value.strip():
            raise arguments_exception("Некорректное имя руководителя")

    @property
    def account_name(self) -> str:
        """Геттер счета."""
        return self.__account_name

    @account_name.setter
    def account_name(self, value: str):
        """Сеттер счета."""
        self._validation_account(value)
        self.__account_name = value.strip()

    def _validation_account(self, value):
        """Проверка, что счет — непустая строка."""
        if not isinstance(value, str) or not value.strip():
            raise arguments_exception("Некорректный счет")

    @property
    def is_first_start(self) -> bool:
        """Флаг первого запуска приложения."""
        return self.__is_first_start

    @is_first_start.setter
    def is_first_start(self, value: bool):
        """Сеттер флага первого запуска."""
        if not isinstance(value, bool):
            raise arguments_exception("Флаг первого старта должен быть bool")
        self.__is_first_start = value