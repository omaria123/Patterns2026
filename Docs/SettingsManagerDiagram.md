# UML-диаграмма: settings_manager

Диаграмма иллюстрирует архитектуру загрузчика настроек приложения:
- Наследование от базового абстрактного класса `abstract_manager`.
- Реализацию паттерна Singleton (`__new__`, `__instance`).
- Ассоциацию с моделью настроек `settings_model` и вложенной организацией `organization_model`.

```mermaid
classDiagram
    class abstract_manager {
        <<abstract>>
        -str _file_name
        -bool _is_loaded
        -dict _data
        +load(file_name: str) None
        +convert() bool
        +is_loaded() bool
    }

    class settings_manager {
        -str __default_file_name
        -settings_model __settings
        -bool __is_loaded
        -dict __data
        -settings_manager __instance
        +__new__() settings_manager
        +load(file_name: str) bool
        +convert() bool
        +is_loaded() bool
        +settings() settings_model
    }

    class settings_model {
        -organization_model __organization
        -str __boss_name
        -str __account_name
        -bool __is_first_start
        +organization organization_model
        +boss_name str
        +account_name str
        +is_first_start bool
    }

    class organization_model {
        -str _inn
        -str _bik
        -str _account
        -str _ownership_form
        +inn str
        +bik str
        +account str
        +ownership_form str
    }

    abstract_manager <|-- settings_manager : Наследование
    settings_manager o-- settings_model : Хранит ссылку
    settings_model *-- organization_model : Включает в себя
```