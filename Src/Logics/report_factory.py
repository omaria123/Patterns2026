from Src.Core.abstract_report_factory import abstract_report_factory
from Src.Core.abstract_report import abstract_report
from Src.Core.exception import arguments_exception
from Src.Dtos.report_type_enum import report_type_enum
from Src.Models.settings_model import settings_model
from Src.Logics.settings_manager import settings_manager

# Импортируем все генераторы отчетов
from Src.Logics.text_report import text_report
from Src.Logics.csv_report import csv_report
from Src.Logics.markdown_report import markdown_report
from Src.Logics.xml_report import xml_report
from Src.Logics.html_report import html_report


class report_factory(abstract_report_factory):
    """
    Фабрика для создания объектов отчетов в зависимости от формата.
    Хранит настройки и поддерживает создание формата по умолчанию (create_default).
    """

    def __init__(self, settings: settings_model = None) -> None:
        """
        Инициализатор фабрики с инкапсуляцией настроек.
        """
        if settings is None:
            sm = settings_manager()
            if not sm.is_loaded:
                sm.load()
            settings = sm.settings

        self.__settings = settings

        # Реестр всех 5 поддерживаемых форматов
        self.__mapping: dict[report_type_enum, type[abstract_report]] = {
            report_type_enum.TXT: text_report,
            report_type_enum.CSV: csv_report,
            report_type_enum.MARKDOWN: markdown_report,
            report_type_enum.XML: xml_report,
            report_type_enum.HTML: html_report,
        }

    @property
    def settings(self) -> settings_model:
        """Геттер инкапсулированных настроек."""
        return self.__settings

    def create(self, report_type: report_type_enum) -> abstract_report:
        """
        Создает инстанс отчета по явно указанному типу.
        """
        if not isinstance(report_type, report_type_enum):
            raise arguments_exception("Тип отчета должен быть элементом report_type_enum", "report_type")

        if report_type not in self.__mapping:
            raise arguments_exception(f"Указанный тип отчета {report_type} не реализован", "report_type")

        report_class = self.__mapping[report_type]
        return report_class()

    def create_default(self) -> abstract_report:
        """
        Создает инстанс отчета в формате по умолчанию из настроек.
        """
        default_format = getattr(self.__settings, "response_format", report_type_enum.MARKDOWN)
        return self.create(default_format)