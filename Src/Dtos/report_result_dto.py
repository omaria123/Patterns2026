from Src.Core.abstract_class import abstract_reference
from Src.Core.exception import arguments_exception


class report_result_dto(abstract_reference):
    """
    DTO для передачи результата отчета (текст или бинарные данные) с метаданными для веб-сервера.
    """

    def __init__(self, text: str = "", binary: list = None) -> None:
        super().__init__()
        self.__text: str = ""
        self.__binary: list = []
        self._mimetype: str = "text/plain"
        self._as_attachment: bool = False
        self._file_name: str = ""

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

    @property
    def mimetype(self) -> str:
        """MIME-тип содержимого для HTTP-заголовка."""
        return self._mimetype

    @mimetype.setter
    def mimetype(self, value: str) -> None:
        self._mimetype = value

    @property
    def as_attachment(self) -> bool:
        """Признак того, что файл должен скачиваться браузером."""
        return self._as_attachment

    @as_attachment.setter
    def as_attachment(self, value: bool) -> None:
        self._as_attachment = value

    @property
    def file_name(self) -> str:
        """Имя файла при скачивании."""
        return self._file_name

    @file_name.setter
    def file_name(self, value: str) -> None:
        self._file_name = value

    @property
    def data(self):
        """Возвращает байты (если файл бинарный) или текст."""
        if self._as_attachment or len(self.__binary) > 0:
            return bytes(self.__binary)
        return self.__text