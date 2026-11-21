from Src.Core.abstract_manager import abstract_manager
from Src.Core.exception import arguments_exception
from Src.Logics.settings_manager import settings_manager
from Src.Models.settings_model import settings_model
from Src.Models.warehouse_model import warehouse_model
from Src.Models.range_model import range_model
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.recipe_model import recipe_model          
from Src.Models.recipe_row_model import recipe_row_model 

from datetime import datetime
from Src.Models.transaction_model import transaction_model

class storage_manager(abstract_manager):
    """
    Менеджер оперативного хранилища данных (In-Memory Repository).
    Реализует паттерн Singleton, наследует abstract_manager.
    Обеспечивает хранение и уникальность моделей данных приложения.
    """
    __instance = None

    def __new__(cls, *args, **kwargs):
        """Паттерн Синглтон: гарантирует существование единственного объекта хранилища."""
        if cls.__instance is None:
            cls.__instance = super(storage_manager, cls).__new__(cls)
            cls.__instance._init_storage()
        return cls.__instance

    def _init_storage(self) -> None:
        """Внутренняя инициализация словарей хранилища."""
        self._warehouses: dict = {}
        self._units: dict = {}
        self._groups: dict = {}
        self._nomenclature: dict = {}
        self._recipes: dict = {}
        self._is_loaded: bool = False
        self._transactions: dict = {}

        self._collections_by_type: dict[type, dict] = {
            warehouse_model: self._warehouses,
            range_model: self._units,
            group_model: self._groups,
            nomenclature_model: self._nomenclature,
            recipe_model: self._recipes,
            transaction_model: self._transactions
        }

    @classmethod
    def clear(cls) -> None:
        """Сброс состояния хранилища (для изоляции модульных тестов)."""
        if cls.__instance is not None:
            cls.__instance._init_storage()
        cls.__instance = None

    def __init__(self, settings: settings_model = None) -> None:
        """Инициализатор: сохраняет переданные настройки."""
        if settings is not None:
            self._settings = settings

    #Доступ к коллекциям через свойства
    @property
    def warehouses(self) -> dict:
        """Коллекция складов {id: warehouse_model}."""
        return self._warehouses

    @property
    def units(self) -> dict:
        """Коллекция единиц измерения {id: range_model}."""
        return self._units

    @property
    def groups(self) -> dict:
        """Коллекция групп номенклатуры {id: group_model}."""
        return self._groups

    @property
    def nomenclature(self) -> dict:
        """Коллекция номенклатуры {id: nomenclature_model}."""
        return self._nomenclature

    @property
    def recipes(self) -> dict:
        """Коллекция технологических карт {id: recipe_model}."""
        return self._recipes

    @property
    def transactions(self) -> dict:
        """Коллекция складских транзакций {id: transaction_model}."""
        return self._transactions

    @property
    def data(self) -> dict:
        """Сводный словарь всех коллекций хранилища."""
        return {
            "warehouses": self._warehouses,
            "units": self._units,
            "groups": self._groups,
            "nomenclature": self._nomenclature,
            "recipes": self._recipes,
            "transactions": self._transactions
        }

    @property
    def is_loaded(self) -> bool:
        """Флаг успешной загрузки / готовности данных."""
        return self._is_loaded

    def domains(self) -> list[str]:
        """Возвращает список ключей (доменных коллекций) хранилища."""
        return list(self.data.keys())


    #Управление добавлением, удалением и обновлением с контролем связей 
    def add(self, item) -> bool:
        """
        Универсальный метод добавления объекта в хранилище с контролем уникальности.
        Возвращает True при успешном добавлении, False если объект уже существует.
        """
        if item is None:
            raise arguments_exception("Добавляемый объект не может быть None", "item")

        target = self._collections_by_type.get(type(item))
        if target is None:
            raise arguments_exception("Попытка добавить неподдерживаемый тип объекта", "item")

        if not getattr(item, "name", "").strip():
            raise arguments_exception("Наименование сущности не может быть пустым", "name")

        # Контроль уникальности: запрет добавления объекта с уже существующим ID
        if item.id in target:
            return False

        target[item.id] = item
        return True

    #Логика первого старта 
    def convert(self, settings: settings_model = None) -> bool:
        """
        Реализация метода convert() из abstract_manager.
        При первом старте формирует первичные справочники системы.
        """
        try:
            # Получаем настройки, если не переданы явно
            if settings is None:
                sm = settings_manager()
                if not sm.is_loaded:
                    sm.load()
                settings = sm.settings

            # Если в настройках первый старт выключен — не наполняем хранилище
            if settings is not None and not settings.is_first_start:
                self._is_loaded = False
                return False

            # Формируем стартовые данные
            self._initialize_default_data()
            self._is_loaded = True
            return True

        except Exception:
            self._is_loaded = False
            return False

    def _initialize_default_data(self) -> None:
        """
        Формирование первичных данных системы при первом старте.
        Все объекты добавляются через метод add с контролем уникальности.
        """
        # 1. Единицы измерения
        gram = range_model("грамм", 1)
        kg = range_model("килограмм", 1000, gram)
        ml = range_model("миллилитр", 1)
        liter = range_model("литр", 1000, ml)
        piece = range_model("штука", 1)

        for u in [gram, kg, ml, liter, piece]:
            self.add(u)

        # 2. Группы номенклатуры
        grocery = group_model("Бакалея")
        dairy = group_model("Молочная продукция")
        sauces = group_model("Соусы")
        greens = group_model("Овощи и зелень")
        dishes = group_model("Готовые блюда")
        packaging = group_model("Упаковка")

        for g in [grocery, dairy, sauces, greens, dishes, packaging]:
            self.add(g)

        # 3. Склады сети
        main_wh = warehouse_model("Центральный склад цеха", "г. Москва, ул. Производственная, д. 5")
        restaurant_wh = warehouse_model("Склад ресторана №1", "г. Москва, ул. Ленина, д. 10")

        self.add(main_wh)
        self.add(restaurant_wh)

        # 4. Номенклатура
        flour = nomenclature_model("Мука пшеничная", "Мука пшеничная в/с для пиццы", grocery, kg)
        yeast = nomenclature_model("Дрожжи сухие", "Дрожжи хлебопекарные сухие быстродействующие", grocery, gram)
        oil = nomenclature_model("Масло оливковое", "Масло оливковое первого отжима Extra Virgin", grocery, ml)
        salt = nomenclature_model("Соль", "Соль поваренная пищевая экстра", grocery, gram)

        cheese = nomenclature_model("Сыр Моцарелла", "Сыр полутвердый Моцарелла 45%", dairy, kg)
        sauce = nomenclature_model("Томатный соус", "Соус томатный натуральный для пиццы", sauces, kg)
        basil = nomenclature_model("Базилик свежий", "Базилик зеленый свежий листовой", greens, gram)

        pizza = nomenclature_model("Пицца Маргарита", "Пицца Маргарита классическая 30 см", dishes, piece)
        box = nomenclature_model("Коробка для пиццы", "Коробка картонная под пиццу 30х30 см", packaging, piece)

        for item in [flour, yeast, oil, salt, cheese, sauce, basil, pizza, box]:
            self.add(item)

        # 5. Технологическая карта
        # Собираем строки через фабричный метод recipe_row_model.create(...)
        row_flour = recipe_row_model.create(flour, brutto=160.0, netto=160.0)
        row_yeast = recipe_row_model.create(yeast, brutto=2.5, netto=2.5)
        row_oil = recipe_row_model.create(oil, brutto=10.0, netto=10.0)
        row_salt = recipe_row_model.create(salt, brutto=3.0, netto=3.0)
        row_sauce = recipe_row_model.create(sauce, brutto=90.0, netto=85.0)
        row_cheese = recipe_row_model.create(cheese, brutto=120.0, netto=115.0)
        row_basil = recipe_row_model.create(basil, brutto=5.0, netto=4.0)
        row_box = recipe_row_model.create(box, brutto=1.0, netto=1.0)  

        # Собираем сам рецепт через фабричный метод recipe_model.create(...)
        pizza_recipe = recipe_model.create(
            name="Технологическая карта: Пицца Маргарита",
            target_item=pizza,
            rows=[
                row_flour, row_yeast, row_oil, row_salt,
                row_sauce, row_cheese, row_basil, row_box
            ]
        )

        self.add(pizza_recipe)

        # 6. Складские транзакции 
        transactions = [
            transaction_model.create(main_wh, flour, kg, 50.0, datetime(2026, 11, 1, 9, 0)),
            transaction_model.create(main_wh, flour, kg, -12.0, datetime(2026, 11, 10, 14, 0)),
            transaction_model.create(main_wh, cheese, kg, 20.0, datetime(2026, 11, 1, 9, 30)),
            transaction_model.create(main_wh, cheese, kg, -5.0, datetime(2026, 11, 12, 16, 0)),
            transaction_model.create(restaurant_wh, flour, kg, 15.0, datetime(2026, 11, 5, 10, 0)),
            transaction_model.create(restaurant_wh, box, piece, 100.0, datetime(2026, 11, 5, 10, 15)),
            transaction_model.create(restaurant_wh, box, piece, -30.0, datetime(2026, 11, 15, 18, 0)),
        ]
        for tx in transactions:
            self.add(tx)

    def load(self, file_name: str = "") -> None:
        """Загрузка данных хранилища (вызывает convert)."""
        self.convert()