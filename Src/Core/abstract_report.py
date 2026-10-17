from abc import ABC, abstractmethod
from Src.Dtos.report_result_dto import report_result_dto
from Src.Core.abstract_class import abstract_reference
from Src.Core.exception import arguments_exception


class abstract_report(ABC):
    """
    Абстрактный класс для формирования отчета.
    Реализует шаблонный метод извлечения данных из любых доменных моделей.
    """

    @abstractmethod
    def build(self, source) -> report_result_dto:
        """Сформировать отчет по источнику данных."""
        pass

    def _get_properties(self, obj) -> list[str]:
        """Вспомогательный метод: извлекает имена всех публичных @property объекта в порядке объявления."""
        props = []

        for cls in type(obj).__mro__:
            for name, attr in cls.__dict__.items():
                if isinstance(attr, property) and not name.startswith("_") and name not in props:
                    props.append(name)
        return props

    def _format_cell_value(self, val) -> str:
        """Вспомогательный метод: форматирует значение ячейки."""
        if val is None:
            return ""
        if hasattr(val, "name") and val.name:
            return str(val.name)
        if hasattr(val, "id"):
            return str(val.id)[:8]
        return str(val)

    def get_report_data(self, source) -> tuple[str, list[str], list[list[str]]]:
        """
        Универсальное извлечение данных из сущности.
        Возвращает: (заголовок, названия колонок, строки данных).
        """
        if source is None or not isinstance(source, abstract_reference):
            raise arguments_exception("Источник отчета должен быть объектом доменной модели", "source")

        title = getattr(source, "name", type(source).__name__)

        # 1. Если у объекта есть табличная часть (rows)
        if hasattr(source, "rows") and isinstance(source.rows, list) and len(source.rows) > 0:
            sample_row = source.rows[0]
            raw_headers = self._get_properties(sample_row)

            headers = [p for p in raw_headers if any(getattr(row, p, "") for row in source.rows)]

            data_rows = []
            for row in source.rows:
                row_values = [self._format_cell_value(getattr(row, prop, "")) for prop in headers]
                data_rows.append(row_values)

            total_row = []
            for col_idx, h in enumerate(headers):
                if col_idx == 0:
                    total_row.append("ИТОГО")
                    continue

                col_values = [getattr(row, h, None) for row in source.rows]
                if all(isinstance(v, (int, float)) for v in col_values):
                    total_row.append(round(sum(col_values), 3))
                else:
                    total_row.append("")

            data_rows.append(total_row)
            return title, headers, data_rows

        # 2. Для одиночной карточки (номенклатура, склад, единица измерения...)
        headers = ["Свойство", "Значение"]
        data_rows = []
        for prop in self._get_properties(source):
            if prop in ("rows", "sub_recipes"):
                continue
            val = getattr(source, prop, "")
            data_rows.append([prop, self._format_cell_value(val)])

        return title, headers, data_rows