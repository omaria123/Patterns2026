from Src.Core.abstract_class import abstract_reference
from Src.Core.exception import arguments_exception


class organization_model(abstract_reference):
    """
    Модель юридического лица (организации).
    Содержит реквизиты: ИНН, БИК, счет, форму собственности.
    """

    def __init__(
        self,
        name: str = "",
        inn: str = "",
        bik: str = "",
        account: str = "",
        ownership_form: str = ""
    ) -> None:
        """
        Инициализатор сущности 'Организация'.

        Параметр name: Наименование организации (строка до 50 символов).
        Параметр inn: ИНН организации (10 или 12 цифр).
        Параметр bik: БИК банка (9 цифр).
        Параметр account: Счет (20 цифр).
        Параметр ownership_form: Форма собственности (ООО, АО и т.д.).
        """
        super().__init__()

        self._inn: str = ""
        self._bik: str = ""
        self._account: str = ""
        self._ownership_form: str = ""

        if name:
            self.name = name
        if inn:
            self.inn = inn
        if bik:
            self.bik = bik
        if account:
            self.account = account
        if ownership_form:
            self.ownership_form = ownership_form

    @property
    def inn(self) -> str:
        """Геттер для получения ИНН организации."""
        return self._inn

    @inn.setter
    def inn(self, value: str) -> None:
        """
        Сеттер для установки ИНН с валидацией длины и формата.

        Параметр: ИНН (строка из 10 или 12 цифр).
        raises arguments_exception: Если передан нестроковый тип или неверный формат.
        """
        if not isinstance(value, str):
            raise arguments_exception("ИНН должен быть строкой", "inn")

        cleaned = value.strip()
        if not cleaned.isdigit() or len(cleaned) not in (10, 12):
            raise arguments_exception("ИНН должен содержать ровно 10 или 12 цифр", "inn")

        self._inn = cleaned

    @property
    def bik(self) -> str:
        """Геттер для получения БИК банка."""
        return self._bik

    @bik.setter
    def bik(self, value: str) -> None:
        """
        Сеттер для установки БИК с валидацией длины и формата.

        Параметр value: БИК банка (строка из 9 цифр).
        raises arguments_exception: Если передан нестроковый тип или не 9 цифр.
        """
        if not isinstance(value, str):
            raise arguments_exception("БИК должен быть строкой", "bik")

        cleaned = value.strip()
        if not cleaned.isdigit() or len(cleaned) != 9:
            raise arguments_exception("БИК должен состоять ровно из 9 цифр", "bik")

        self._bik = cleaned

    @property
    def account(self) -> str:
        """Геттер для получения счета."""
        return self._account

    @account.setter
    def account(self, value: str) -> None:
        """
        Сеттер для установки расчетного счета с валидацией.

        Параметр value: Номер счета (строка из 20 цифр).
        raises arguments_exception: Если передан нестроковый тип или не 20 цифр.
        """
        if not isinstance(value, str):
            raise arguments_exception("Счет должен быть строкой", "account")

        cleaned = value.strip()
        if not cleaned.isdigit() or len(cleaned) != 20:
            raise arguments_exception("Расчетный счет должен состоять ровно из 20 цифр", "account")

        self._account = cleaned

    @property
    def ownership_form(self) -> str:
        """Геттер для получения формы собственности."""
        return self._ownership_form

    @ownership_form.setter
    def ownership_form(self, value: str) -> None:
        """
        Сеттер для установки формы собственности.

        Параметр value: Строковое обозначение (например, 'ООО').
        raises arguments_exception: Если передана пустая строка или неверный тип.
        """
        if not isinstance(value, str):
            raise arguments_exception("Форма собственности должна быть строкой", "ownership_form")

        cleaned = value.strip()
        if not cleaned:
            raise arguments_exception("Форма собственности не может быть пустой", "ownership_form")

        self._ownership_form = cleaned