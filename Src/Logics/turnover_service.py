from datetime import timedelta

from Src.Core.abstract_manager import abstract_manager
from Src.Core.exception import arguments_exception
from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.turnover_dto import turnover_dto
from Src.Logics.prototype import prototype
from Src.Logics.storage_manager import storage_manager


class turnover_service:
    """Сервис формирования оборотно-сальдовой ведомости (ОСВ) на базе шаблона Прототип."""

    def __init__(self, storage: abstract_manager | None = None) -> None:
        """Инициализирует сервис ОСВ с внедрением хранилища."""
        if storage is not None and not isinstance(storage, abstract_manager):
            raise arguments_exception("Хранилище должно наследовать abstract_manager", "storage")
        self._storage = storage if storage is not None else storage_manager()

    def build(self, filter_model: filter_dto) -> list[turnover_dto]:
        """Формирует список строк ОСВ с учетом фильтрации через шаблон Прототип."""
        if filter_model is None or not isinstance(filter_model, filter_dto):
            raise arguments_exception("Фильтр должен быть объектом filter_dto", "filter_model")

        transactions = list(self._storage.data.get("transactions", {}).values())
        proto = prototype(transactions)

        # Фильтруем транзакции по сущностям 
        matched_proto = self._filter_by_entities(proto, filter_model)

        # Через clone() разделяем транзакции ДО начала периода и ЗА период
        opening_txs = []
        if filter_model.start_period is not None:
            before_filter = filter_dto(end_period=filter_model.start_period - timedelta(microseconds=1))
            opening_txs = matched_proto.clone(before_filter).data

        period_filter = filter_dto(
            start_period=filter_model.start_period,
            end_period=filter_model.end_period
        )
        turnover_txs = matched_proto.clone(period_filter).data

        # Агрегируем обороты в разрезе (склад, номенклатура)
        groups: dict[tuple, turnover_dto] = {}

        for tx in opening_txs:
            key = (tx.warehouse.id, tx.nomenclature.id)
            dto = groups.setdefault(key, self._create_empty_dto(tx))
            dto.opening_balance += self._normalize_value(tx)

        for tx in turnover_txs:
            key = (tx.warehouse.id, tx.nomenclature.id)
            dto = groups.setdefault(key, self._create_empty_dto(tx))
            val = self._normalize_value(tx)
            if val > 0:
                dto.income += val
            else:
                dto.outcome += abs(val)

        return list(groups.values())

    def _filter_by_entities(self, proto: prototype, filter_model: filter_dto) -> prototype:
        """Применяет фильтр к самим транзакциям или их вложенным сущностям через Прототип."""
        entity_filter = filter_dto(
            name=filter_model.name,
            unique_code=filter_model.unique_code,
            filter_type=filter_model.filter_type,
            nested=filter_model.nested
        )

        if filter_model.nested is None and (filter_model.name or filter_model.unique_code):
            return proto.clone(filter_dto(nested=entity_filter))

        return proto.clone(entity_filter)

    def _create_empty_dto(self, tx) -> turnover_dto:
        """Создает пустую строку ОСВ для пары."""
        target_unit = tx.nomenclature.unit if tx.nomenclature and tx.nomenclature.unit else tx.unit
        return turnover_dto.create(
            warehouse=tx.warehouse,
            nomenclature=tx.nomenclature,
            unit=target_unit,
            opening_balance=0.0,
            income=0.0,
            outcome=0.0
        )

    def _normalize_value(self, tx) -> float:
        """Пересчитывает количество транзакции в единицу измерения карточки номенклатуры."""
        nom_unit = tx.nomenclature.unit if tx.nomenclature else None
        if nom_unit is None or tx.unit is None or tx.unit == nom_unit:
            return float(tx.value)
        return float(tx.value) * float(tx.unit.conversion_factor) / float(nom_unit.conversion_factor)