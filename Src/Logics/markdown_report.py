from Src.Core.abstract_report import abstract_report
from Src.Core.exception import arguments_exception
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.recipe_model import recipe_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model


class markdown_report(abstract_report):
    """
    Генератор отчета в формате Markdown-таблицы.
    Формирует бинарные данные для скачивания файла.
    """

    def build(self, source) -> report_result_dto:
        result = report_result_dto()
        content = ""

        if isinstance(source, recipe_model):
            content += f"# Технологическая карта: {source.name}\n\n"
            content += "| Код | Наименование | Брутто (г) | Нетто (г) |\n"
            content += "| :--- | :--- | :--- | :--- |\n"
            for row in source.rows:
                r_id = str(row.nomenclature.id)[:8] if row.nomenclature else ""
                r_name = row.nomenclature.name if row.nomenclature else ""
                content += f"| {r_id} | {r_name} | {row.brutto} | {row.netto} |\n"
            content += f"\n**ИТОГО:** Брутто = {source.brutto_weight} г, Нетто = {source.netto_weight} г\n"

        elif isinstance(source, nomenclature_model):
            content += f"# Номенклатура: {source.name}\n\n"
            content += "| Поле | Значение |\n| :--- | :--- |\n"
            content += f"| ID | {source.id} |\n"
            content += f"| Полное наименование | {source.full_name} |\n"
            content += f"| Группа | {source.group.name if source.group else '-'} |\n"
            content += f"| Единица | {source.unit.name if source.unit else '-'} |\n"

        elif isinstance(source, range_model):
            content += f"# Единица измерения: {source.name}\n\n"
            content += "| Поле | Значение |\n| :--- | :--- |\n"
            content += f"| ID | {source.id} |\n"
            content += f"| Коэффициент | {source.conversion_factor} |\n"
            content += f"| Базовая единица | {source.base_unit.name if source.base_unit else '-'} |\n"

        else:
            raise arguments_exception("Неподдерживаемый тип источника данных для отчета", "source")

        # Формируем бинарные данные
        result.binary = list(content.encode("utf-8"))
        return result