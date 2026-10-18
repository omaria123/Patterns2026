from Src.Core.abstract_class import abstract_reference


class report_data_dto(abstract_reference):
    """
    DTO для передачи структурированных табличных данных отчета.
    Содержит заголовок, названия колонок и строки данных.
    """

    def __init__(
        self,
        title: str = "",
        headers: list[str] | None = None,
        rows: list[list] | None = None
    ) -> None:
        super().__init__()
        self._title = title
        self._headers = headers if headers is not None else []
        self._rows = rows if rows is not None else []

    @property
    def title(self) -> str:
        """Заголовок отчета."""
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        self._title = value

    @property
    def headers(self) -> list[str]:
        """Названия колонок таблицы."""
        return self._headers

    @headers.setter
    def headers(self, value: list[str]) -> None:
        self._headers = value

    @property
    def rows(self) -> list[list]:
        """Строки данных таблицы."""
        return self._rows

    @rows.setter
    def rows(self, value: list[list]) -> None:
        self._rows = value