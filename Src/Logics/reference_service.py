from typing import Any
from uuid import UUID

from Src.Core.abstract_class import abstract_reference
from Src.Core.abstract_manager import abstract_manager
from Src.Core.abstract_service import abstract_service
from Src.Core.exception import arguments_exception
from Src.Logics.convert_factory import convert_factory
from Src.Logics.deserialize_factory import deserialize_factory
from Src.Logics.storage_manager import storage_manager


class reference_service(abstract_service):
    """
    Сервисный слой для управления доменными сущностями (CRUD).
    Инкапсулирует валидацию, сериализацию и индекс обратных ссылок.
    """

    def __init__(
        self,
        storage: abstract_manager | None = None,
        convertor: convert_factory | None = None,
        deserializer: deserialize_factory | None = None
    ) -> None:
        """Инициализирует сервис, внедряет зависимости и строит индекс связей."""
        if storage is not None and not isinstance(storage, abstract_manager):
            raise arguments_exception("Хранилище должно наследовать abstract_manager", "storage")
        if convertor is not None and not isinstance(convertor, convert_factory):
            raise arguments_exception("Конвертор должен быть объектом convert_factory", "convertor")
        if deserializer is not None and not isinstance(deserializer, deserialize_factory):
            raise arguments_exception("Десериализатор должен быть объектом deserialize_factory", "deserializer")

        self._storage = storage if storage is not None else storage_manager()
        self._convertor = convertor if convertor is not None else convert_factory()
        self._deserializer = deserializer if deserializer is not None else deserialize_factory()

        # Индекс обратных ссылок {id_целевой_сущности: {id_ссылающихся_сущностей}}
        self._ref_index: dict[UUID, set[UUID]] = {}
        # Кэш соответствия ключа домена классу модели 
        self._domain_types: dict[str, type] = {}
        self.rebuild_index()

    def rebuild_index(self) -> None:
        """Перестраивает индекс обратных ссылок по всем коллекциям хранилища."""
        self._ref_index.clear()
        self._domain_types.clear()

        for domain_key, collection in self._storage.data.items():
            if not isinstance(collection, dict):
                continue
            if collection:
                self._domain_types[domain_key] = type(next(iter(collection.values())))
            for item in collection.values():
                self._index_item(item)

    def _get_properties(self, obj: Any) -> list[str]:
        """Извлекает имена публичных @property объекта по цепочке MRO."""
        props = []
        for cls in type(obj).__mro__:
            for name, attr in cls.__dict__.items():
                if isinstance(attr, property) and not name.startswith("_") and name not in props:
                    props.append(name)
        return props

    def _is_stored_entity(self, obj: abstract_reference) -> bool:
        """Проверяет, является ли объект самостоятельной сущностью в хранилище."""
        return any(obj.id in col for col in self._storage.data.values() if isinstance(col, dict))

    def _collect_ref_ids(self, obj: Any, owner_id: UUID, visited: set[int]) -> set[UUID]:
        """Собирает UUID связанных сущностей через публичные свойства."""
        if obj is None or id(obj) in visited:
            return set()
        visited.add(id(obj))

        refs: set[UUID] = set()
        if isinstance(obj, abstract_reference):
            for prop_name in self._get_properties(obj):
                val = getattr(obj, prop_name, None)
                if isinstance(val, abstract_reference) and val.id != owner_id:
                    refs.add(val.id)
                elif isinstance(val, (list, tuple)):
                    for element in val:
                        if isinstance(element, abstract_reference) and element.id != owner_id:
                            if self._is_stored_entity(element):
                                refs.add(element.id)
                            else:
                                # Для составных строк обходим вложенные ссылки
                                refs.update(self._collect_ref_ids(element, owner_id, visited))
        return refs

    def _index_item(self, item: abstract_reference) -> None:
        """Добавляет исходящие ссылки сущности в обратный индекс."""
        for ref_id in self._collect_ref_ids(item, item.id, set()):
            self._ref_index.setdefault(ref_id, set()).add(item.id)

    def _unindex_item(self, item: abstract_reference) -> None:
        """Удаляет исходящие ссылки сущности из обратного индекса."""
        for ref_id in self._collect_ref_ids(item, item.id, set()):
            owners = self._ref_index.get(ref_id)
            if owners:
                owners.discard(item.id)
                if not owners:
                    del self._ref_index[ref_id]

    def _get_collection_by_class(self, model_cls: type) -> dict:
        """Находит словарь хранилища для указанного класса доменной модели."""
        if not isinstance(model_cls, type) or not issubclass(model_cls, abstract_reference):
            raise arguments_exception("Ожидается класс-наследник abstract_reference", "model_cls")

        for domain_key, collection in self._storage.data.items():
            known_cls = self._domain_types.get(domain_key)
            if known_cls is None and collection:
                known_cls = type(next(iter(collection.values())))
                self._domain_types[domain_key] = known_cls
            if known_cls is model_cls:
                return collection

        raise arguments_exception(f"Коллекция для модели '{model_cls.__name__}' не найдена", "model_cls")

    def resolve_model_type(self, domain_name: str) -> type:
        """Определяет класс доменной модели по строковому имени домена или класса."""
        if not isinstance(domain_name, str) or not domain_name.strip():
            raise arguments_exception("Тип сущности должен быть непустой строкой", "domain_name")

        key = domain_name.strip()
        if key in self._domain_types:
            return self._domain_types[key]

        if key in self._storage.data and self._storage.data[key]:
            cls = type(next(iter(self._storage.data[key].values())))
            self._domain_types[key] = cls
            return cls

        return self._deserializer._resolve_model_class(key)

    def get_domains(self) -> list[str]:
        """Возвращает список ключей доменных коллекций хранилища."""
        return self._storage.domains()

    def get_list(self, model_cls: type) -> list:
        """Возвращает список всех сущностей указанного класса модели."""
        collection = self._get_collection_by_class(model_cls)
        return list(collection.values())

    def get_by_id(self, model_cls: type, entity_id: UUID) -> abstract_reference | None:
        """Возвращает доменную сущность по классу модели и UUID."""
        if not isinstance(entity_id, UUID):
            raise arguments_exception("Идентификатор должен быть объектом UUID", "entity_id")

        collection = self._get_collection_by_class(model_cls)
        return collection.get(entity_id)

    def is_referenced(self, item: abstract_reference) -> bool:
        """Проверяет, ссылаются ли другие сущности на переданный объект."""
        if item is None or not isinstance(item, abstract_reference):
            raise arguments_exception("Сущность должна наследовать abstract_reference", "item")

        return bool(self._ref_index.get(item.id))

    def add(self, item: abstract_reference) -> bool:
        """Добавляет готовую доменную сущность в хранилище и обновляет индекс связей."""
        if item is None or not isinstance(item, abstract_reference):
            raise arguments_exception("Объект должен наследовать abstract_reference", "item")

        added = self._storage.add(item)
        if added:
            self._index_item(item)
        return added

    def update(self, entity_id: UUID, item: abstract_reference) -> bool:
        """Обновляет сущность с запретом смены кода при наличии входящих связей."""
        if not isinstance(entity_id, UUID):
            raise arguments_exception("Идентификатор должен быть объектом UUID", "entity_id")
        if item is None or not isinstance(item, abstract_reference):
            raise arguments_exception("Сущность должна наследовать abstract_reference", "item")
        if not getattr(item, "name", "").strip():
            raise arguments_exception("Наименование сущности не может быть пустым", "name")

        collection = self._get_collection_by_class(type(item))
        existing = collection.get(entity_id)
        if existing is None:
            return False

        # Запрещаем смену кода (ID), если на сущность есть входящие ссылки
        if item.id != existing.id:
            if self.is_referenced(existing):
                raise arguments_exception(
                    f"Запрещено менять код сущности '{existing.name}', так как она связана с другими данными",
                    "id"
                )
            if item.id in collection:
                raise arguments_exception(f"Сущность с кодом '{item.id}' уже существует", "id")
            del collection[existing.id]

        self._unindex_item(existing)
        collection[item.id] = item
        self._index_item(item)
        return True

    def delete(self, item: abstract_reference) -> bool:
        """Удаляет сущность из хранилища, если на нее нет входящих ссылок."""
        if item is None or not isinstance(item, abstract_reference):
            raise arguments_exception("Сущность должна наследовать abstract_reference", "item")

        collection = self._get_collection_by_class(type(item))
        existing = collection.get(item.id)
        if existing is None:
            return False

        if self.is_referenced(existing):
            raise arguments_exception(
                f"Запрещено удалять сущность '{existing.name}', так как она связана с другими данными",
                "id"
            )

        self._unindex_item(existing)
        del collection[existing.id]
        return True

    def serialize(self, obj: Any) -> Any:
        """Сериализует объект или коллекцию через единый convert_factory."""
        return self._convertor.convert(obj)