from typing import Any
from uuid import UUID

from Src.Core.abstract_class import abstract_reference
from Src.Core.abstract_deserialize_factory import abstract_deserialize_factory
from Src.Core.exception import arguments_exception
import json

class deserialize_factory(abstract_deserialize_factory):
    """
    Фабрика десериализации данных JSON в доменные модели.
    Автоматически определяет тип модели по структуре данных и предотвращает дублирование через Cache.
    """

    def __init__(self) -> None:
        """Инициализатор фабрики. Подготавливает кеш объектов."""
        self._cache: dict[UUID, abstract_reference] = {}

    @property
    def cache(self) -> dict[UUID, abstract_reference]:
        """Кеш созданных объектов для предотвращения дублирования в памяти."""
        return self._cache

    def clear_cache(self) -> None:
        """Очистить кеш объектов."""
        self._cache.clear()

    def _get_all_domain_models(self) -> list[type]:
        """Автоматический поиск всех наследников abstract_reference."""
        models = []

        def _collect(base_cls):
            for sub in base_cls.__subclasses__():
                models.append(sub)
                _collect(sub)

        _collect(abstract_reference)
        return models

    def _get_model_properties(self, cls: type) -> set[str]:
        """Динамически извлекает имена всех публичных @property и методов добавления."""
        props = set()
        for parent in cls.__mro__:
            for name, attr in parent.__dict__.items():
                if isinstance(attr, property) and not name.startswith("_"):
                    props.add(name)
                # Учитываем методы добавления коллекций 
                if name.startswith("add_") and callable(attr):
                    props.add(name.replace("add_", "") + "s")
        return props

    def determine_type(self, data: dict) -> type:
        """
        Автоматически определяет класс модели по набору ключей словаря.
        """
        data_keys = set(data.keys()) - {"id"}
        models = self._get_all_domain_models()

        candidates = [
            cls for cls in models
            if data_keys.issubset(self._get_model_properties(cls))
        ]

        if not candidates:
            raise arguments_exception(
                f"Не удалось определить доменную модель для полей: {list(data.keys())}", "data"
            )

        return min(candidates, key=lambda cls: len(self._get_model_properties(cls) - data_keys))

    def _is_read_only_property(self, instance: Any, prop_name: str) -> bool:
        """Проверяет, является ли свойство read-only."""
        prop = getattr(type(instance), prop_name, None)
        return isinstance(prop, property) and prop.fset is None

    def deserialize(self, data: Any, target_type: Any = None) -> Any:
        """
        Главный метод десериализации.
        Принимает словарь или список и возвращает восстановленные объекты.
        """
        if isinstance(data, str):
            data = json.loads(data)

        if data is None:
            return None

        # Если передан список - десериализуем каждый элемент списка
        if isinstance(data, list):
            return [self.deserialize(item, target_type) for item in data]

        if not isinstance(data, dict):
            return data

        # Определение класса: если тип передан явно - берем его, иначе определяем по данным
        if isinstance(target_type, type) and issubclass(target_type, abstract_reference):
            model_cls = target_type
        elif isinstance(target_type, str):
            clean_name = target_type.strip().lower().replace("_model", "")
            matched = [
                cls for cls in self._get_all_domain_models()
                if cls.__name__.lower().replace("_model", "") == clean_name
            ]
            model_cls = matched[0] if matched else self.determine_type(data)
        else:
            model_cls = self.determine_type(data)

        # Исключаем дубликаты объектов в памяти
        obj_id = None
        if "id" in data and data["id"]:
            obj_id = UUID(str(data["id"])) if not isinstance(data["id"], UUID) else data["id"]
            if obj_id in self._cache:
                return self._cache[obj_id]

        # Создаем экземпляр модели и сразу регистрируем в кеше
        instance = model_cls()
        if obj_id is not None:
            instance.id = obj_id
            self._cache[obj_id] = instance

        # Сортируем ключи так, чтобы brutto шло перед netto 
        sorted_items = sorted(data.items(), key=lambda kv: 1 if kv[0] == "netto" else 0)

        # Заполняем свойства модели
        for key, value in sorted_items:
            if key == "id":
                continue

            # Строки рецептов - добавляем через метод add_*
            if isinstance(value, list):
                add_method = getattr(instance, f"add_{key[:-1]}", getattr(instance, f"add_{key}", None))
                if callable(add_method):
                    for item in value:
                        child = self.deserialize(item)
                        add_method(child)
                    continue

            if self._is_read_only_property(instance, key):
                continue

            # Вложенные модели: рекурсивно десериализуем
            if isinstance(value, dict):
                child = self.deserialize(value)
                if hasattr(instance, key):
                    setattr(instance, key, child)
                continue

            # Восстановление циклической базовой единицы
            if key == "base_unit" and value is None and hasattr(instance, "base_unit"):
                instance.base_unit = instance
                continue

            # Установка простых свойств
            if hasattr(instance, key):
                if key == "name" and isinstance(value, str) and not value.strip():
                    continue
                try:
                    setattr(instance, key, value)
                except (AttributeError, arguments_exception):
                    pass

        return instance