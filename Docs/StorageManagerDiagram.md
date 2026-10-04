# UML-диаграмма: storage_manager

Диаграмма иллюстрирует архитектуру оперативного хранилища данных (In-Memory Repository):
- Наследование базового контракта `abstract_manager`.
- Реализацию шаблона проектирования `<<Singleton>>`.
- Хранение коллекций 4 доменных моделей.

```mermaid
classDiagram
    class abstract_manager {
        <<abstract>>
        -str _file_name
        -bool _is_loaded
        -dict _data
        +load(file_name) void
        +convert() bool
        +is_loaded() bool
    }

    class storage_manager {
        <<Singleton>>
        -dict _warehouses
        -dict _units
        -dict _groups
        -dict _nomenclature
        -bool _is_loaded
        -storage_manager __instance
        +add(item) bool
        +convert(settings) bool
        +load(file_name) void
        +warehouses() dict
        +units() dict
        +groups() dict
        +nomenclature() dict
        +data() dict
        +is_loaded() bool
        -_initialize_default_data() void
    }

    class warehouse_model {
        -str _address
        +address() str
    }

    class range_model {
        -float _conversion_factor
        -range_model _base_unit
        +conversion_factor() float
        +base_unit() range_model
    }

    class group_model {
        +name() str
    }

    class nomenclature_model {
        -str _full_name
        -group_model _group
        -range_model _unit
        +full_name() str
        +group() group_model
        +unit() range_model
    }

    abstract_manager <|-- storage_manager : "Наследование"
    storage_manager o-- warehouse_model : "Склады"
    storage_manager o-- range_model : "Единицы измерения"
    storage_manager o-- group_model : "Группы"
    storage_manager o-- nomenclature_model : "Номенклатура"
```