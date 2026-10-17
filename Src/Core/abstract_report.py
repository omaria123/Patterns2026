from abc import ABC, abstractmethod
from Src.Dtos.report_result_dto import report_result_dto


class abstract_report(ABC):
    """Абстрактный класс для формирования отчета."""

    @abstractmethod
    def build(self, source) -> report_result_dto:
        """Сформировать отчет по источнику данных."""
        pass