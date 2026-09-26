from Src.Core.abstract_class import abstract_reference
from Src.Core.exception import arguments_exception
import pytest

class test_entity(abstract_reference):
    """Тестовый класс-наследник для проверки абстрактного класса."""
    pass 

def test_abstract_model_net_id_not_null():
    """Проверка, что id создается не пустым."""
    entity = test_entity()
    result = entity.id
    assert result != ""

def test_abstract_model_unique_id():
    """Проверка, что у двух разных сущностей разные id."""
    entity1 = test_entity()
    entity2 = test_entity()

    assert entity1.id != entity2.id

def test_abstract_model_not_repit():
    """Проверка сравнения двух сущностей с одинаковым id."""
    entity1 = test_entity()
    entity1.id = "rrr"

    entity2 = test_entity()
    entity2.id = "rrr"

    assert entity1 == entity2

def test_abstract_model_empty_name_exception():
    """Проверка, что пустая строка вызывает исключение (старый вариант через try)."""
    entity = test_entity()

    try:
        entity.name = ""
        assert False 
    except Exception:
        assert True

def test_abstract_model_arguments_exception_raised():
    """Проверка arguments_exception"""
    entity = test_entity()
    
    with pytest.raises(arguments_exception):
        entity.name = "   "