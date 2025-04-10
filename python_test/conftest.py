import os
from typing import Any, Generator

import pytest
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver

from data_helper.api_helper import UserApiHelper, SpendsHttpClient
from databases.spend_db import SpendDb
from model.config import Envs
from model.db.spend import SpendAdd
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


@pytest.fixture(scope='session')
def app_user(envs: Envs):
    UserApiHelper(envs.sign_up_url).create_user(user_name=envs.test_username, user_password=envs.test_password)


@pytest.fixture(scope="session")
def spend_db(envs) -> SpendDb:
    return SpendDb(envs.spend_db_url)


@pytest.fixture(scope='module')
def web_driver() -> Generator[WebDriver, Any, None]:
    wd = webdriver.Chrome()
    wd.maximize_window()
    yield wd
    wd.quit()


@pytest.fixture(scope='module')
def auth(web_driver: WebDriver, app_user, envs):
    niffler = Niffler(web_driver)
    niffler.login_page.go_to_niffler()
    niffler.login_page.login_by_exist_user(envs.test_username, envs.test_password)
    assert niffler.main_page.is_page_load(), 'Главная страница не прогрузилась'
    local_storage = niffler.login_page.wd.execute_script('return window.localStorage;')
    token = local_storage['access_token']
    spends_client = SpendsHttpClient(envs.gateway_url, token, envs.test_username)
    yield niffler, spends_client


@pytest.fixture(scope='module')
def niffler(auth: tuple[Niffler, SpendsHttpClient]) -> Generator[Niffler, Any, None]:
    niffler, _ = auth
    yield niffler


@pytest.fixture(scope='module')
def spends_client(auth: tuple[Niffler, SpendsHttpClient]) -> SpendsHttpClient:
    _, spends_client = auth
    return spends_client


@pytest.fixture(params=[])
def category(request, spends_client: SpendsHttpClient, spend_db: SpendDb):
    test_category = spends_client.add_category(request.param['category_name'], request.param['archived'])
    yield test_category
    all_categories_ids = spends_client.get_ids_all_categories()
    if test_category.id in all_categories_ids:
        spend_db.delete_category(test_category.id)


@pytest.fixture(params=[])
def spend(request, spends_client: SpendsHttpClient) -> Generator[SpendAdd, Any, None]:
    category_name, amount = request.param['category'], request.param['amount']
    currency, desc = 'RUB', ''
    if 'currency' in request.param.keys():
        currency = request.param['currency']
    if 'desc' in request.param.keys():
        desc = request.param['desc']
    test_spend = spends_client.add_spend(category=category_name, amount=amount, currency=currency, desc=desc)
    yield test_spend
    all_spends = spends_client.get_ids_all_spending()
    if test_spend.id in all_spends:
        spends_client.delete_spending_by_id(test_spend.id)
