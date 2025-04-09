import os
from typing import Any, Generator

import pytest
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver

from data_helper.api_helper import UserApiHelper, SpendsHttpClient
from model.niffler import Niffler


@pytest.fixture(scope="session")
def envs():
    load_dotenv()


@pytest.fixture(scope="session")
def frontend_url(envs) -> str:
    return os.getenv("FRONTEND_URL")


@pytest.fixture(scope="session")
def sign_up_url(envs) -> str:
    return os.getenv("SIGN_UP_URL")


@pytest.fixture(scope="session")
def gateway_url(envs) -> str:
    return os.getenv("GATEWAY_URL")


@pytest.fixture(scope='session')
def app_user(envs, sign_up_url: str) -> tuple[str, str]:
    user_name, password = os.getenv("TEST_USERNAME"), os.getenv("TEST_PASSWORD")
    UserApiHelper(sign_up_url).create_user(user_name=user_name, user_password=password)
    return user_name, password


@pytest.fixture(scope='module')
def web_driver() -> Generator[WebDriver, Any, None]:
    wd = webdriver.Chrome()
    wd.maximize_window()
    yield wd
    wd.quit()


@pytest.fixture(scope='module')
def auth(web_driver: WebDriver, gateway_url: str, app_user: tuple[str, str]):
    niffler = Niffler(web_driver)
    user_name, password = app_user
    niffler.login_page.go_to_niffler()
    niffler.login_page.login_by_exist_user(user_name, password)
    assert niffler.main_page.is_page_load(), 'Главная страница не прогрузилась'
    local_storage = niffler.login_page.wd.execute_script('return window.localStorage;')
    token = local_storage['access_token']
    spends_client = SpendsHttpClient(gateway_url, token, user_name)
    yield niffler, spends_client


@pytest.fixture(scope='module')
def niffler(auth: tuple[Niffler, SpendsHttpClient]) -> Generator[Niffler, Any, None]:
    niffler, _ = auth
    yield niffler


@pytest.fixture(scope='module')
def spends_client(auth: tuple[Niffler, SpendsHttpClient]) -> SpendsHttpClient:
    _, spends_client = auth
    return spends_client
