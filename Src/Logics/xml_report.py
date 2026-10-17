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
        result = report_result_dto()
        lines = ['<?xml version="1.0" encoding="UTF-8"?>']

        if isinstance(source, recipe_model):
            lines.append(f'<recipe id="{source.id}" name="{source.name}">')
            lines.append(f'  <totals brutto="{source.brutto_weight}" netto="{source.netto_weight}"/>')
            lines.append('  <ingredients>')
            for row in source.rows:
                r_id = row.nomenclature.id if row.nomenclature else ""
                r_name = row.nomenclature.name if row.nomenclature else ""
                lines.append(f'    <item id="{r_id}" name="{r_name}" brutto="{row.brutto}" netto="{row.netto}"/>')
            lines.append('  </ingredients>')
            lines.append('</recipe>')

        elif isinstance(source, nomenclature_model):
            g_name = source.group.name if source.group else ""
            u_name = source.unit.name if source.unit else ""
            lines.append(f'<nomenclature id="{source.id}">')
            lines.append(f'  <name>{source.name}</name>')
            lines.append(f'  <full_name>{source.full_name}</full_name>')
            lines.append(f'  <group>{g_name}</group>')
            lines.append(f'  <unit>{u_name}</unit>')
            lines.append('</nomenclature>')

        elif isinstance(source, range_model):
            b_name = source.base_unit.name if source.base_unit else ""
            lines.append(f'<unit id="{source.id}">')
            lines.append(f'  <name>{source.name}</name>')
            lines.append(f'  <conversion_factor>{source.conversion_factor}</conversion_factor>')
            lines.append(f'  <base_unit>{b_name}</base_unit>')
            lines.append('</unit>')

        else:
            raise arguments_exception("Неподдерживаемый тип источника данных для отчета", "source")

        result.text = "\n".join(lines)
        return result