from typing import Any
from uuid import UUID

from Src.Core.abstract_class import abstract_reference
from Src.Core.abstract_has_references import abstract_has_references
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

    def _index_item(self, item: abstract_reference) -> None:
        """Добавляет исходящие ссылки сущности в обратный индекс."""
        if not isinstance(item, abstract_has_references):
            return

        for ref in item.get_references():
            if ref is not None and getattr(ref, "id", None) is not None and ref.id != item.id:
                self._ref_index.setdefault(ref.id, set()).add(item.id)

    def _unindex_item(self, item: abstract_reference) -> None:
        """Удаляет исходящие ссылки сущности из обратного индекса."""
        if not isinstance(item, abstract_has_references):
            return

        for ref in item.get_references():
            if ref is None or getattr(ref, "id", None) is None:
                continue
            owners = self._ref_index.get(ref.id)
            if owners:
                owners.discard(item.id)
                if not owners:
                    del self._ref_index[ref.id]

    def _resolve_collection(self, entity_type: str) -> tuple[dict, type | None]:
        """Динамически определяет коллекцию и класс модели"""
        if not isinstance(entity_type, str) or not entity_type.strip():
            raise arguments_exception("Тип сущности должен быть непустой строкой", "entity_type")

        key = entity_type.strip()

        # 1. Прямой поиск по ключам хранилища 
        if key in self._storage.data:
            collection = self._storage.data[key]
            model_cls = self._domain_types.get(key)
            if model_cls is None and collection:
                model_cls = type(next(iter(collection.values())))
                self._domain_types[key] = model_cls
            return collection, model_cls

        # 2. Поиск по имени модели среди наследников abstract_reference 
        model_cls = self._deserializer._resolve_model_class(key)
        for domain_key, collection in self._storage.data.items():
            known_cls = self._domain_types.get(domain_key)
            if known_cls is None and collection:
                known_cls = type(next(iter(collection.values())))
            if known_cls is model_cls:
                return collection, model_cls

        raise arguments_exception(f"Неизвестный тип сущности: '{entity_type}'", "entity_type")

    def _extract_id(self, item_or_id: Any) -> UUID:
        """Извлекает и валидирует UUID из объекта модели или строки."""
        if item_or_id is None:
            raise arguments_exception("Идентификатор не может быть пустым", "id")

        raw_id = item_or_id.id if hasattr(item_or_id, "id") else item_or_id
        if isinstance(raw_id, UUID):
            return raw_id
        if isinstance(raw_id, str) and raw_id.strip():
            try:
                return UUID(raw_id.strip())
            except ValueError:
                raise arguments_exception(f"Некорректный формат UUID: '{raw_id}'", "id")

        raise arguments_exception("Некорректный тип идентификатора", "id")

    def get_domains(self) -> list[str]:
        """Возвращает список ключей доменных коллекций хранилища."""
        return self._storage.domains()

    def get_list(self, entity_type: str) -> list:
        """Возвращает список всех сущностей указанного типа."""
        collection, _ = self._resolve_collection(entity_type)
        return list(collection.values())

    def get_by_id(self, entity_type: str, entity_id: str | UUID) -> abstract_reference | None:
        """Возвращает доменную сущность по типу и коду или None, если не найдена."""
        collection, _ = self._resolve_collection(entity_type)
        target_id = self._extract_id(entity_id)
        return collection.get(target_id)

    def is_referenced(self, item_or_id: Any) -> bool:
        """Проверяет, ссылаются ли другие сущности на переданный объект или код."""
        target_id = self._extract_id(item_or_id)
        return bool(self._ref_index.get(target_id))

    def add(self, item: abstract_reference) -> bool:
        """Добавляет готовую доменную сущность в хранилище и обновляет индекс связей."""
        if item is None or not isinstance(item, abstract_reference):
            raise arguments_exception("Объект должен наследовать abstract_reference", "item")

        added = self._storage.add(item)
        if added:
            self._index_item(item)
        return added

    def create(self, entity_type: str, data: dict) -> abstract_reference:
        """Десериализует, валидирует и сохраняет новую доменную сущность."""
        if not isinstance(data, dict) or not data:
            raise arguments_exception("Данные для создания должны быть непустым словарем", "data")

        collection, expected_cls = self._resolve_collection(entity_type)
        entity = self._deserializer.deserialize(data, target_type=expected_cls)

        if expected_cls is not None and not isinstance(entity, expected_cls):
            raise arguments_exception(f"Сущность не соответствует типу '{entity_type}'", "type")

        if not self._storage.add(entity):
            raise arguments_exception(f"Сущность с кодом '{entity.id}' уже существует", "id")

        if entity_type.strip() in self._storage.data and expected_cls is None:
            self._domain_types[entity_type.strip()] = type(entity)

        self._index_item(entity)
        return entity

    def update(self, entity_type: str, entity_id: str | UUID, data: dict) -> abstract_reference | None:
        """Обновляет сущность с запретом смены кода при наличии входящих связей."""
        if not isinstance(data, dict) or not data:
            raise arguments_exception("Данные для обновления должны быть непустым словарем", "data")

        collection, expected_cls = self._resolve_collection(entity_type)
        existing = self.get_by_id(entity_type, entity_id)
        if existing is None:
            return None

        payload = dict(data)
        if "id" not in payload or not payload["id"]:
            payload["id"] = str(existing.id)

        target_cls = expected_cls if expected_cls is not None else type(existing)
        new_item = self._deserializer.deserialize(payload, target_type=target_cls)

        if type(new_item) is not type(existing):
            raise arguments_exception("Несовпадение типа обновляемой сущности", "type")

        if not getattr(new_item, "name", "").strip():
            raise arguments_exception("Наименование сущности не может быть пустым", "name")

        # Запрещаем смену кода (ID), если на сущность есть ссылки
        if new_item.id != existing.id:
            if self.is_referenced(existing.id):
                raise arguments_exception(
                    f"Запрещено менять код сущности '{existing.name}', так как она связана с другими данными",
                    "id"
                )
            if new_item.id in collection:
                raise arguments_exception(f"Сущность с кодом '{new_item.id}' уже существует", "id")
            del collection[existing.id]

        self._unindex_item(existing)
        collection[new_item.id] = new_item
        self._index_item(new_item)
        return new_item

    def delete(self, entity_type: str, entity_id: str | UUID) -> bool:
        """Удаляет сущность из хранилища, если на нее нет входящих ссылок."""
        collection, _ = self._resolve_collection(entity_type)
        existing = self.get_by_id(entity_type, entity_id)
        if existing is None:
            return False

        if self.is_referenced(existing.id):
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