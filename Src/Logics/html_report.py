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
        if source is None:
            raise arguments_exception("Источник данных не может быть None", "source")

        title, headers, data_rows = self.get_report_data(source)

        html = ["<!DOCTYPE html><html><head><meta charset='utf-8'><title>Отчет</title></head><body>"]
        html.append(f"<h2>{title}</h2>")
        html.append("<table border='1' cellpadding='5' cellspacing='0'>")
        html.append("<tr>" + "".join(f"<th>{h}</th>" for h in headers) + "</tr>")

        for row in data_rows:
            html.append("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>")

        html.append("</table></body></html>")

        result = report_result_dto()
        result.text = "".join(html)
        result.mimetype = "text/html"
        result.as_attachment = False
        return result