import pytest

from python_test.data_helper.api_helper import create_user


@pytest.fixture(scope='session', autouse=True)
def prepare_admin_user() -> tuple[str, str]:
    user_name = 'admin'
    password = 'admin'
    create_user(user_name=user_name, user_password=password)
    return user_name, password
