class arguments_exception(Exception):
    """Исключение, выбрасываемое при некорректных аргументах."""
    __stack_trace: str = ""
    __message: str = ""
    __field: str = ""

    def __init__(self, message: str, field: str = "", stack_trace: str = ""):
        self.__field = field.strip() if field else ""
        self.__message = message.strip() if message else ""
        self.__stack_trace = stack_trace.strip() if stack_trace else ""
        super().__init__(self.__message)

    def __str__(self):
        field_info = f" в поле '{self.__field}'" if self.__field else ""
        return f"Ошибка: Некорректный аргумент{field_info}! Сообщение: {self.__message}\n{self.__stack_trace}"