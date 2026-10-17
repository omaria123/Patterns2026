from enum import Enum 

class report_type_enum(Enum):
    """
    Перечисление поддерживаемых форматов отчетов.
    """
    TXT = "txt"
    CSV = "csv"
    MARKDOWN = "markdown"
    XML = "xml"
    HTML = "html"