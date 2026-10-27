from typing import Any
from Src.Core.abstract_class import abstract_reference
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.exception import arguments_exception
from Src.Core.abstract_factory import abstract_factory

class reference_convertor(abstract_convertor):
    """
    Конвертор для доменных моделей, унаследованных от abstract_reference.
    Формирует вложенный словарь {field: {свойства_модели}}.
    """

    def __init__(self, factory: abstract_factory = None) -> None:
        """Инициализатор конвертора"""
        self._factory: abstract_factory | None = None
        if factory is not None:
            self.factory = factory

    @property
    def factory(self) -> abstract_factory | None:
        """Геттер ссылки на фабрику конверторов."""
        return self._factory

    @factory.setter
    def factory(self, value: abstract_factory) -> None:
        """Сеттер ссылки на фабрику конверторов."""
        if value is not None and not isinstance(value, abstract_factory):
            raise arguments_exception("Фабрика должна наследовать abstract_factory", "factory")
        self._factory = value

    def _get_properties(self, obj: Any) -> list[str]:
        """Извлекает публичные @property объекта."""
        props = []
        for cls in type(obj).__mro__:
            for name, attr in cls.__dict__.items():
                if isinstance(attr, property) and not name.startswith("_") and name not in props:
                    props.append(name)
        return props

    def convert(self, field: str, obj: Any, visited: set | None = None) -> dict:
        """
        Преобразует доменную модель в словарь с рекурсивным обходом свойств.
        """

        # Валидация имени поля
        if not isinstance(field, str):
            raise arguments_exception("Наименование поля должно быть непустой строкой", "field")

        # Валидация типа объекта
        if not isinstance(obj, abstract_reference):
            raise arguments_exception(
                f"Объект поля '{field}' должен наследовать abstract_reference", "obj"
            )

        # Защита от зацикливания 
        if visited is None:
            visited = set()

        obj_id = str(obj.id)
        if obj_id in visited:
            return {field.strip(): None} if field.strip() else None

        current_visited = set(visited)
        current_visited.add(obj_id)

        if self._factory is None:
            model_dict = {"id": str(obj.id), "name": str(obj.name)}
            return {field.strip(): model_dict} if field.strip() else model_dict

        model_dict = {}
        properties = self._get_properties(obj)

        for prop_name in properties:
            prop_value = getattr(obj, prop_name, None)

            if prop_value is None:
                model_dict[prop_name] = None
            elif isinstance(prop_value, list):
                item_list = []
                for item in prop_value:
                    item_convertor = self._factory.create(item)
                    res = item_convertor.convert("", item, visited=current_visited)
                    item_list.append(res.get("", res))
                model_dict[prop_name] = item_list
            elif isinstance(prop_value, abstract_reference) and (prop_value is obj or str(prop_value.id) in current_visited):
                model_dict[prop_name] = None
            else:
                prop_convertor = self._factory.create(prop_value)
                converted_field = prop_convertor.convert(prop_name, prop_value, visited=current_visited)
                model_dict.update(converted_field)

        return {field.strip(): model_dict} if field.strip() else model_dict