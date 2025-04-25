import pytest

from python_test.data_helper.oauth_client import OAuthClient
from python_test.model.config import Envs


@pytest.fixture(scope="session")
def auth_token(envs: Envs) -> str:
    return OAuthClient(envs).get_token(envs.test_username, envs.test_password)
