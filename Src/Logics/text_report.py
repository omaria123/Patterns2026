from Src.Core.abstract_report import abstract_report
from Src.Core.exception import arguments_exception
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.recipe_model import recipe_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model


class text_report(abstract_report):
    """
    Генератор текстового отчета.
    """

    def build(self, source) -> report_result_dto:
        if source is None:
            raise arguments_exception("Источник данных не может быть None", "source")

        data = self.get_report_data(source)

        lines = [f"{data.title}\n", " | ".join(data.headers), "-" * 50]
        for row in data.rows:
            lines.append(" | ".join(str(cell) for cell in row))

        result = report_result_dto()
        result.text = "\n".join(lines)
        result.mimetype = "text/plain"
        result.as_attachment = False
        return result