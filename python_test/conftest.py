import os

import pytest
from dotenv import load_dotenv
from selenium import webdriver

from data_helper.api_helper import UserApiHelper, SpendsHttpClient
from databases.spend_db import SpendDb
from model.config import Envs
from model.niffler import Niffler


@pytest.fixture(scope="session", autouse=True)
def envs() -> Envs:
    load_dotenv()
    return Envs(
        frontend_url=os.getenv("FRONTEND_URL"),
        gateway_url=os.getenv("GATEWAY_URL"),
        sign_up_url=os.getenv('SIGN_UP_URL'),
        spend_db_url=os.getenv("SPEND_DB_URL"),
        test_username=os.getenv("TEST_USERNAME"),
        test_password=os.getenv("TEST_PASSWORD")
    )


@pytest.fixture(scope="session")
def app_user(envs):
    user_name, password = os.getenv("TEST_USERNAME"), os.getenv("TEST_PASSWORD")
    UserApiHelper(envs.sign_up_url).create_user(user_name=user_name, user_password=password)
    return user_name, password


@pytest.fixture(scope='module')
def auth(app_user: tuple[str, str]):
    wd = webdriver.Chrome()
    wd.maximize_window()
    niffler = Niffler(wd)
    user_name, password = app_user
    niffler.go_to_niffler()
    niffler.login_page.login_by_exist_user(user_name, password)
    local_storage = niffler.wd.execute_script('return window.localStorage;')
    token = local_storage['access_token']
    yield niffler, token, {'user': user_name, 'password': password}


@pytest.fixture(scope='module')
def spends_client(envs: Envs, auth):
    _, token, user = auth
    return SpendsHttpClient(envs.gateway_url, token, user["user"])


@pytest.fixture(scope="session")
def spend_db(envs) -> SpendDb:
    return SpendDb(envs.spend_db_url)
