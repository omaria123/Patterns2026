from Src.Core.abstract_report import abstract_report
from Src.Core.exception import arguments_exception
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.recipe_model import recipe_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model


class html_report(abstract_report):
    """
    Генератор отчета в формате HTML (структурированный текст для браузера).
    """

    def build(self, source) -> report_result_dto:
        result = report_result_dto()
        html = ["<!DOCTYPE html><html><head><meta charset='utf-8'><title>Отчет</title></head><body>"]

        if isinstance(source, recipe_model):
            html.append(f"<h2>Технологическая карта: {source.name}</h2>")
            html.append("<table border='1' cellpadding='5' cellspacing='0'>")
            html.append("<tr><th>Код</th><th>Наименование</th><th>Брутто (г)</th><th>Нетто (г)</th></tr>")
            for row in source.rows:
                r_id = str(row.nomenclature.id)[:8] if row.nomenclature else ""
                r_name = row.nomenclature.name if row.nomenclature else ""
                html.append(f"<tr><td>{r_id}</td><td>{r_name}</td><td>{row.brutto}</td><td>{row.netto}</td></tr>")
            html.append(f"<tr><th colspan='2'>ИТОГО</th><th>{source.brutto_weight}</th><th>{source.netto_weight}</th></tr>")
            html.append("</table>")

        elif isinstance(source, nomenclature_model):
            html.append(f"<h2>Номенклатура: {source.name}</h2>")
            html.append("<table border='1' cellpadding='5'>")
            html.append(f"<tr><td>ID</td><td>{source.id}</td></tr>")
            html.append(f"<tr><td>Полное имя</td><td>{source.full_name}</td></tr>")
            html.append(f"<tr><td>Группа</td><td>{source.group.name if source.group else '-'}</td></tr>")
            html.append(f"<tr><td>Единица</td><td>{source.unit.name if source.unit else '-'}</td></tr>")
            html.append("</table>")

        elif isinstance(source, range_model):
            html.append(f"<h2>Единица измерения: {source.name}</h2>")
            html.append("<table border='1' cellpadding='5'>")
            html.append(f"<tr><td>ID</td><td>{source.id}</td></tr>")
            html.append(f"<tr><td>Коэффициент</td><td>{source.conversion_factor}</td></tr>")
            html.append(f"<tr><td>Базовая единица</td><td>{source.base_unit.name if source.base_unit else '-'}</td></tr>")
            html.append("</table>")

        else:
            raise arguments_exception("Неподдерживаемый тип источника данных для отчета", "source")

        html.append("</body></html>")
        result.text = "".join(html)
        return result