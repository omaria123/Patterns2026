# UML-диаграмма моделей технологических карт (рецептов)

Диаграмма иллюстрирует архитектуру доменных моделей для хранения и расчета рецептов:
- Наследование от базового абстрактного класса `abstract_reference`.
- Композицию рецепта (`recipe_model`) и его строк (`recipe_row_model`).
- Связи с номенклатурой (`nomenclature_model`) для целевого блюда и ингредиентов.
- Хранение технологических карт в центральном репозитории `storage_manager`.

```mermaid
classDiagram
    class abstract_reference {
        <<abstract>>
        -UUID _id
        -str _name
        +id() UUID
        +name() str
    }

    class recipe_model {
        -nomenclature_model _target_item
        -list _rows
        +target_item() nomenclature_model
        +rows() list
        +brutto_weight() float
        +netto_weight() float
        +add_row(row) bool
        +delete_row(row) bool
        +create(name, target_item, rows)$ recipe_model
    }

    class recipe_row_model {
        -nomenclature_model _nomenclature
        -float _brutto
        -float _netto
        +nomenclature() nomenclature_model
        +brutto() float
        +netto() float
        +create(nomenclature, brutto, netto)$ recipe_row_model
    }

    class nomenclature_model {
        -str _full_name
        +full_name() str
    }

    class storage_manager {
        <<Singleton>>
        -dict _recipes
        +recipes() dict
    }

    abstract_reference <|-- recipe_model : "Наследование"
    abstract_reference <|-- recipe_row_model : "Наследование"

    recipe_model *-- recipe_row_model : "Содержит строки"
    recipe_model --> nomenclature_model : "Целевое блюдо"
    recipe_row_model --> nomenclature_model : "Ингредиент"

    storage_manager o-- recipe_model : "Хранит рецепты"
```