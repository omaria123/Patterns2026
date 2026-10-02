import pytest
from Src.Models.organization_model import organization_model
from Src.Core.exception import arguments_exception


def test_success_organization_model_create_valid_data():
    """
    Проверка успешного создания организации со всеми корректными реквизитами.
    """
    # Arrange
    name = "ООО Ромашка"
    inn = "1234567890"               # 10 цифр
    bik = "044525225"                # 9 цифр
    account = "40702810400000001234" # 20 цифр
    ownership = "ООО"

    # Act
    org = organization_model(
        name=name,
        inn=inn,
        bik=bik,
        account=account,
        ownership_form=ownership
    )

    # Assert
    assert org.name == name
    assert org.inn == inn
    assert org.bik == bik
    assert org.account == account
    assert org.ownership_form == ownership
    assert org.id is not None


def test_throw_arguments_exception_organization_invalid_inn():
    """ Проверка выброса исключения arguments_exception при неверной длине ИНН."""
    # Arrange
    invalid_inn = "12345"  # Слишком короткий

    # Act & Assert
    with pytest.raises(arguments_exception):
        organization_model(inn=invalid_inn)


def test_throw_arguments_exception_organization_invalid_bik():
    """ Проверка выброса исключения arguments_exception при наличии букв в БИК. """
    # Arrange
    invalid_bik = "04452522А"  # Содержит букву

    # Act & Assert
    with pytest.raises(arguments_exception):
        organization_model(bik=invalid_bik)


def test_throw_arguments_exception_organization_invalid_account():
    """ Проверка выброса исключения arguments_exception при неверной длине счета. """
    # Arrange
    invalid_account = "40702810"  # Не 20 цифр

    # Act & Assert
    with pytest.raises(arguments_exception):
        organization_model(account=invalid_account)