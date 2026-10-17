from Src.Core.abstract_report import abstract_report
from Src.Core.exception import arguments_exception
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.recipe_model import recipe_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model


class text_report(abstract_report):
    """
    Генератор текстового отчета по технологическим картам, номенклатуре и единицам измерения.
    """

    def build(self, source) -> report_result_dto:
        """
        Сформировать текстовый отчет по переданной модели.
        """
        result = report_result_dto()

        # Если передан рецепт
        if isinstance(source, recipe_model):
            header = f"Технологическая карта: {source.name}\n"
            columns = "Код | Наименование | Брутто | Нетто\n"
            data = ""
            for item in source.rows:
                item_id = str(item.nomenclature.id)[:8] if item.nomenclature else "N/A"
                item_name = item.nomenclature.name if item.nomenclature else "N/A"
                data += f"{item_id} | {item_name} | {item.brutto} | {item.netto}\n"
            totals = f"ИТОГО: Брутто = {source.brutto_weight} г | Нетто = {source.netto_weight} г\n"
            result.text = f"{header}{columns}{data}{totals}".strip()

        # Если передана номенклатура
        elif isinstance(source, nomenclature_model):
            g_name = source.group.name if source.group else "N/A"
            u_name = source.unit.name if source.unit else "N/A"
            lines = [
                f"Номенклатура: {source.name}",
                f"Код: {source.id}",
                f"Полное наименование: {source.full_name}",
                f"Группа: {g_name}",
                f"Единица измерения: {u_name}"
            ]
            result.text = "\n".join(lines)

        # Если передана единица измерения
        elif isinstance(source, range_model):
            b_name = source.base_unit.name if source.base_unit else "N/A"
            lines = [
                f"Единица измерения: {source.name}",
                f"Код: {source.id}",
                f"Коэффициент пересчета: {source.conversion_factor}",
                f"Базовая единица: {b_name}"
            ]
            result.text = "\n".join(lines)

        else:
            raise arguments_exception("Неподдерживаемый тип источника данных для отчета", "source")

        return result