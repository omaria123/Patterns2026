from typing import Any
from uuid import UUID
import importlib
import json
import inspect

from Src.Core.abstract_class import abstract_reference
from Src.Core.abstract_deserialize_factory import abstract_deserialize_factory
from Src.Core.exception import arguments_exception

class deserialize_factory(abstract_deserialize_factory):
    """
    Фабрика десериализации данных JSON в доменные модели.
    Автоматически определяет тип модели по структуре данных и предотвращает дублирование через Cache.
    """

    def __init__(self, storage: storage_manager = None) -> None:
        """Инициализатор фабрики. Подготавливает кеш объектов."""
        self._storage = storage 
        self._local_cache: dict[UUID, abstract_reference] = {}

    @property
    def storage(self) -> storage_manager:
        """Ссылка на инкапсулированное хранилище."""
        return self._storage

    @property
    def cache(self) -> dict[UUID, abstract_reference]:
        """Кеш объектов: объединяет данные storage_manager и локально созданные сущности."""
        result = dict(self._local_cache)
        if hasattr(self._storage, "data") and isinstance(self._storage.data, dict):
            for collection in self._storage.data.values():
                if isinstance(collection, dict):
                    for k, v in collection.items():
                        uid = UUID(str(k)) if not isinstance(k, UUID) else k
                        result[uid] = v
        return result

    def clear_cache(self) -> None:
        """Очистить кеш объектов."""
        self._local_cache.clear()

    def _find_in_cache(self, obj_id: UUID) -> abstract_reference | None:
        """Поиск объекта в инкапсулированном кеше storage_manager и локальном."""
        if obj_id in self._local_cache:
            return self._local_cache[obj_id]

        if self._storage is not None and hasattr(self._storage, "data") and isinstance(self._storage.data, dict):
            for collection in self._storage.data.values():
                if isinstance(collection, dict):
                    if obj_id in collection:
                        return collection[obj_id]
                    if str(obj_id) in collection:
                        return collection[str(obj_id)]
        return None

    def _save_to_cache(self, obj_id: UUID, instance: abstract_reference) -> None:
        """Сохранение объекта в локальный кеш и в хранилище storage_manager."""
        self._local_cache[obj_id] = instance
        if self._storage is not None and hasattr(self._storage, "add"):
            try:
                self._storage.add(instance)
            except Exception:
                pass

    def _resolve_model_class(self, type_str: str) -> type:
        """Определяет класс модели по его полному имени из поля 'type'."""
        if "." in type_str:
            module_name, class_name = type_str.rsplit(".", 1)
            try:
                module = importlib.import_module(module_name)
                cls = getattr(module, class_name)
                if isinstance(cls, type) and issubclass(cls, abstract_reference):
                    return cls
            except (ImportError, AttributeError):
                pass

        def _get_subclasses(cls):
            subs = []
            for s in cls.__subclasses__():
                subs.append(s)
                subs.extend(_get_subclasses(s))
            return subs

        clean_type = type_str.lower().replace("_model", "")
        for cls in _get_subclasses(abstract_reference):
            cls_name = cls.__name__.lower().replace("_model", "")
            if cls.__name__.lower() == type_str.lower() or f"{cls.__module__}.{cls.__qualname__}" == type_str or cls_name == clean_type:
                return cls

        raise arguments_exception(f"Не удалось найти класс модели для типа '{type_str}'", "type")
    
    def _is_read_only_property(self, instance: Any, prop_name: str) -> bool:
        """Проверяет, является ли свойство read-only."""
        prop = getattr(type(instance), prop_name, None)
        return isinstance(prop, property) and prop.fset is None

    def _build_constructor_args(self, model_cls: type, data: dict) -> dict:
        """Определяет аргументы конструктора."""
        sig = inspect.signature(model_cls.__init__)
        args = {}

        for param_name, param in sig.parameters.items():
            if param_name in ("self", "args", "kwargs"):
                continue

            if param_name in data:
                val = data[param_name]
                if isinstance(val, dict):
                    args[param_name] = self.deserialize(val, target_type=param_name)
                elif isinstance(val, list):
                    args[param_name] = [self.deserialize(item) if isinstance(item, dict) else item for item in val]
                else:
                    args[param_name] = val
            elif param.default is not inspect.Parameter.empty:
                args[param_name] = param.default

        return args


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

        # Определение класса: берем из поля 'type' или из target_type
        if "type" in data and isinstance(data["type"], str):
            model_cls = self._resolve_model_class(data["type"])
        elif isinstance(target_type, type) and issubclass(target_type, abstract_reference):
            model_cls = target_type
        elif isinstance(target_type, str):
            model_cls = self._resolve_model_class(target_type)
        else:
            raise arguments_exception("В данных отсутствует поле 'type' и не передан target_type", "data")

        # Исключаем дубликаты объектов в памяти
        obj_id = None
        if "id" in data and data["id"]:
            obj_id = UUID(str(data["id"])) if not isinstance(data["id"], UUID) else data["id"]
            cached_obj = self._find_in_cache(obj_id)
            if cached_obj is not None:
                return cached_obj

        args = self._build_constructor_args(model_cls, data)
        try:
            instance = model_cls(**args)
        except Exception:
            instance = model_cls()

        if obj_id is not None:
            instance.id = obj_id
            self._save_to_cache(obj_id, instance)

         # Заполняем свойства модели, которые не вошли в __init__
        for key, value in data.items():
            if key in args or key in ("id", "type"):
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
                child = self.deserialize(value, target_type=key)
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