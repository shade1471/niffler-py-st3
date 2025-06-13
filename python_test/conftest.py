import os
import sys
from pathlib import Path
from typing import Any, Generator

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

import pytest
from allure_commons.reporter import AllureReporter
from allure_pytest.listener import AllureListener
from dotenv import load_dotenv
from pytest import FixtureDef, FixtureRequest
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver

from python_test.data_helper.api_helper import UserApiHelper, SpendsHttpClient
from python_test.data_helper.kafka_client import KafkaClient
from python_test.databases.spend_db import SpendDb
from python_test.model.config import Envs
from python_test.model.db.category import Category
from python_test.model.db.spend import SpendAdd
from python_test.model.niffler import Niffler

pytest_plugins = ["fixtures.auth_fixtures", "fixtures.client_fixtures"]


def allure_logger(config) -> AllureReporter:
    listener: AllureListener = config.pluginmanager.get_plugin("allure_listener")
    return listener.allure_logger


@pytest.hookimpl(hookwrapper=True, trylast=True)
def pytest_fixture_setup(fixturedef: FixtureDef, request: FixtureRequest):
    yield
    logger = allure_logger(request.config)
    item = logger.get_last_item()
    scope_letter = fixturedef.scope[0].upper()
    normalize_fix_name = " ".join(fixturedef.argname.split("_")).title()
    item.name = f'[{scope_letter}] {normalize_fix_name}'


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_teardown(item):
    yield
    reporter = allure_logger(item.config)
    test = reporter.get_test(None)
    test.labels = list(filter(lambda x: x.name not in ("suite", "subSuite", "parentSuite"), test.labels))


@pytest.fixture(scope="session", autouse=True)
def envs() -> Envs:
    load_dotenv()
    return Envs(
        frontend_url=os.getenv("FRONTEND_URL"),
        gateway_url=os.getenv("GATEWAY_URL"),
        auth_url=os.getenv('AUTH_URL'),
        auth_secret=os.getenv("AUTH_SECRET"),
        spend_db_url=os.getenv("SPEND_DB_URL"),
        test_username=os.getenv("TEST_USERNAME"),
        test_password=os.getenv("TEST_PASSWORD"),
        kafka_address=os.getenv("KAFKA_ADDRESS"),
        userdata_db_url=os.getenv('USERDATA_DB_URL')
    )


@pytest.fixture(scope='session', autouse=True)
def app_user(envs: Envs):
    UserApiHelper(envs).create_user(user_name=envs.test_username, user_password=envs.test_password)


@pytest.fixture(scope='module')
def web_driver() -> Generator[WebDriver, Any, None]:
    wd = webdriver.Chrome()
    wd.maximize_window()
    yield wd
    wd.quit()


@pytest.fixture(scope='module')
def niffler(web_driver: WebDriver, app_user, envs) -> Generator[Niffler, Any, None]:
    niffler = Niffler(web_driver)
    niffler.login_page.go_to_niffler()
    niffler.login_page.login_by_exist_user(envs.test_username, envs.test_password)
    assert niffler.main_page.is_page_load(), 'Главная страница не прогрузилась'
    yield niffler


@pytest.fixture(params=[])
def category(request: FixtureRequest, spends_client: SpendsHttpClient, spend_db: SpendDb) -> Generator[
    Category, Any, None]:
    test_category = spends_client.add_category(**request.param)
    yield test_category
    all_categories_ids = spends_client.get_ids_all_categories()
    if test_category.id in all_categories_ids:
        spend_db.delete_category(test_category.id)


@pytest.fixture(params=[])
def spend(request: FixtureRequest, spends_client: SpendsHttpClient) -> Generator[SpendAdd, Any, None]:
    test_spend = spends_client.add_spend(**request.param)
    yield test_spend
    all_spends = spends_client.get_ids_all_spending()
    if test_spend.id in all_spends:
        spends_client.delete_spending_by_id(test_spend.id)


@pytest.fixture(scope="session")
def kafka(envs):
    """Взаимодействие с Kafka"""
    with KafkaClient(envs) as k:
        yield k
