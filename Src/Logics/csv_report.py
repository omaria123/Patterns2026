from Src.Core.abstract_report import abstract_report
from Src.Core.exception import arguments_exception
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.recipe_model import recipe_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model


class csv_report(abstract_report):
    """
    Генератор отчета в формате CSV.
    Формирует бинарные данные для скачивания файла.
    """

    def build(self, source) -> report_result_dto:
        if source is None:
            raise arguments_exception("Источник данных не может быть None", "source")

        data = self.get_report_data(source)

        lines = [";".join(data.headers)]
        for row in data.rows:
            formatted_row = [str(cell).replace(".", ",") for cell in row]
            lines.append(";".join(formatted_row))

        result = report_result_dto()
        result.binary = list("\n".join(lines).encode("utf-8-sig"))
        result.mimetype = "text/csv"
        result.as_attachment = True
        result.file_name = "report.csv"
        return result