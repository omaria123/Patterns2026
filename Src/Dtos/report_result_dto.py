from Src.Core.abstract_class import abstract_reference
from Src.Core.exception import arguments_exception


class report_result_dto(abstract_reference):
    """
    DTO для передачи результата отчета (текст или бинарные данные).
    """

    def __init__(self, text: str = "", binary: list = None) -> None:
        super().__init__()
        self.__text: str = ""
        self.__binary: list = []

        if text:
            self.text = text
        if binary:
            self.binary = binary

    @property
    def text(self) -> str:
        """Геттер текстового содержимого отчета."""
        return self.__text

    @text.setter
    def text(self, value: str) -> None:
        """Сеттер текста отчета."""
        if not isinstance(value, str):
            raise arguments_exception("Текст отчета должен быть строкой", "text")
        self.__text = value
        self.__binary = []

    @property
    def binary(self) -> list:
        """Геттер бинарных данных отчета."""
        return self.__binary

    @binary.setter
    def binary(self, value: list) -> None:
        """Сеттер бинарных данных отчета."""
        if not isinstance(value, list):
            raise arguments_exception("Бинарные данные должны быть списком", "binary")
        self.__binary = value
        self.__text = ""