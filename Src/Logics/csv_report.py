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
        result = report_result_dto()
        lines = []

        if isinstance(source, recipe_model):
            lines.append("Код;Наименование;Брутто;Нетто")
            for row in source.rows:
                r_id = str(row.nomenclature.id)[:8] if row.nomenclature else ""
                r_name = row.nomenclature.name if row.nomenclature else ""
                brutto_val = str(row.brutto).replace(".", ",")
                netto_val = str(row.netto).replace(".", ",")
                lines.append(f"{r_id};{r_name};{brutto_val};{netto_val}")
            
            total_brutto = str(source.brutto_weight).replace(".", ",")
            total_netto = str(source.netto_weight).replace(".", ",")
            lines.append(f"ИТОГО;;{total_brutto};{total_netto}")

        elif isinstance(source, nomenclature_model):
            lines.append("Код;Краткое наименование;Полное наименование;Группа;Единица")
            g_name = source.group.name if source.group else ""
            u_name = source.unit.name if source.unit else ""
            lines.append(f"{str(source.id)[:8]};{source.name};{source.full_name};{g_name};{u_name}")

        elif isinstance(source, range_model):
            lines.append("Код;Наименование;Коэффициент;Базовая единица")
            b_name = source.base_unit.name if source.base_unit else ""
            factor_val = str(source.conversion_factor).replace(".", ",")
            lines.append(f"{str(source.id)[:8]};{source.name};{factor_val};{b_name}")

        else:
            raise arguments_exception("Неподдерживаемый тип источника данных для отчета", "source")

        csv_content = "\n".join(lines)
        # Формируем бинарные данные для скачивания
        result.binary = list(csv_content.encode("utf-8-sig"))
        return result