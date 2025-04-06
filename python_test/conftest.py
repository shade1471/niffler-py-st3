import os

import pytest
from dotenv import load_dotenv
from selenium import webdriver

from data_helper.api_helper import UserApiHelper, SpendsHttpClient
from model.niffler import Niffler


@pytest.fixture(scope="session", autouse=True)
def envs():
    load_dotenv()


@pytest.fixture(scope="session")
def frontend_url(envs):
    return os.getenv("FRONTEND_URL")


@pytest.fixture(scope="session")
def sign_up_url(envs):
    return os.getenv("SIGN_UP_URL")


@pytest.fixture(scope="session")
def gateway_url(envs):
    return os.getenv("GATEWAY_URL")


@pytest.fixture(scope="session")
def app_user(envs):
    user_name, password = os.getenv("TEST_USERNAME"), os.getenv("TEST_PASSWORD")
    UserApiHelper(os.getenv('SIGN_UP_URL')).create_user(user_name=user_name, user_password=password)
    return user_name, password


@pytest.fixture(scope='module')
def auth(frontend_url: str, sign_up_url: str, app_user: tuple[str, str]):
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
def spends_client(gateway_url: str, auth):
    _, token, user = auth
    return SpendsHttpClient(gateway_url, token, user["user"])
