from abc import ABC

"""
Абстрактный класс для реализации загрузки и обработки данных
"""
class abstract_manager(ABC):
    # Полный путь к файлу
    __file_name:str = ""
    # Флаг. Загрузка и обработка завершена успешно
    __is_loaded:bool = False
    # Загруженные сырые данные
    __data:list = [] 
   
    """
    Загрузить данные
    """
    def load(self, file_name:str = "") -> None:
        pass

    """
    Обработать загруженные данные
    """    
    def convert(self) -> bool:
        return False

    """
    Флаг. Данные подготовлены
    """
    @property
    def is_loaded(self) -> bool:
        return self.__is_loaded  