from Src.Core.abstract_report import abstract_report
from Src.Core.exception import arguments_exception
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.recipe_model import recipe_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model


class xml_report(abstract_report):
    """
    Генератор отчета в формате XML (структурированный текст).
    """

    def build(self, source) -> report_result_dto:
        if source is None:
            raise arguments_exception("Источник данных не может быть None", "source")

        data = self.get_report_data(source)

        lines = ['<?xml version="1.0" encoding="UTF-8"?>']
        lines.append(f'<report title="{data.title}">')
        lines.append('  <items>')

        for row in data.rows:
            lines.append('    <item>')
            for h, cell in zip(data.headers, row):
                tag = str(h).strip().lower().replace(" ", "_")
                lines.append(f'      <{tag}>{cell}</{tag}>')
            lines.append('    </item>')

        lines.append('  </items>')
        lines.append('</report>')

        result = report_result_dto()
        result.text = "\n".join(lines)
        result.mimetype = "application/xml"
        result.as_attachment = False
        return result