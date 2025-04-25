import pytest

from python_test.data_helper.api_helper import SpendsHttpClient
from python_test.databases.spend_db import SpendDb
from python_test.model.config import Envs


@pytest.fixture(scope="session")
def spends_client(envs: Envs, auth_token: str) -> SpendsHttpClient:
    return SpendsHttpClient(envs, auth_token, envs.test_username)


@pytest.fixture(scope="session")
def spend_db(envs: Envs) -> SpendDb:
    return SpendDb(envs)
