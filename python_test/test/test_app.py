import logging
import uuid
from datetime import datetime, timedelta

import pytest
from faker.proxy import Faker
from selenium import webdriver

from python_test.data_helper.api_helper import create_user, UserApiHelper
from python_test.model.MainPage import MainPage
from python_test.model.niffler import Niffler

NEW_USER = f'{Faker().first_name()}{uuid.uuid4().__str__()[0:4]}'
PASSWORD = Faker().password(length=5)
TEST_CATEGORY = {'name': 'auto', 'username': NEW_USER}


def prepare_test_data(token):
    api_helper = UserApiHelper(token)
    api_helper.add_spend(NEW_USER, 'category1', 10000)
    api_helper.add_spend(NEW_USER, 'category2', 1000)
    api_helper.add_spend(NEW_USER, 'category2', 1000)
    api_helper.add_spend(NEW_USER, 'category3', 50)
    api_helper.add_spend(NEW_USER, 'category3', 1000)
    api_helper.add_spend(NEW_USER, 'category3', 4000)
    api_helper.add_spend(NEW_USER, 'past spending', 300, date=datetime(2020, 12, 31))
    api_helper.add_spend(NEW_USER, 'past spending', 700, date=datetime(2021, 1, 1))
    api_helper.add_spend(NEW_USER, 'past spending', 700, date=datetime.now() - timedelta(days=9))


class TestSpending:

    @pytest.fixture(scope="class")
    def browser(self, prepare_admin_user):
        user_name, password = prepare_admin_user
        wd = webdriver.Chrome()
        wd.maximize_window()
        niffler = Niffler(wd)
        niffler.login_page.go_to_niffler()
        niffler.login_page.login_by_exist_user(user_name, password)
        assert niffler.main_page.is_page_load()
        local_storage = niffler.main_page.wd.execute_script('return window.localStorage;')
        token = local_storage['access_token']
        api_helper = UserApiHelper(token)
        api_helper.remove_all_spending()
        api_helper.add_spend(user_name, 'books', 500)
        yield niffler
        api_helper.remove_all_spending()
        wd.quit()

    def test_add_spending_gui(self, browser):
        browser.main_page.go_to_niffler()
        count_before = browser.main_page.get_count_spending_on_main_page()
        browser.main_page.add_new_spending(50000, 'study')
        assert browser.main_page.get_count_spending_on_main_page() == count_before + 1

    def test_required_spending_fields(self, browser):
        browser.main_page.go_to_niffler()
        browser.main_page.click_add_spending()
        browser.spending_page.click_save()
        assert browser.spending_page.get_amount_field_helper_text() == 'Amount has to be not less then 0.01'
        assert browser.spending_page.get_category_field_helper_text() == 'Please choose category'


class TestSearch:

    @pytest.fixture(scope="class")
    def browser(self):
        create_user(user_name=NEW_USER, user_password=PASSWORD)
        logging.info(f'Создана учетная запись {NEW_USER}/{PASSWORD}')
        wd = webdriver.Chrome()
        wd.maximize_window()
        niffler = Niffler(wd)
        niffler.login_page.go_to_niffler()
        niffler.login_page.login_by_exist_user(NEW_USER, PASSWORD)
        assert niffler.main_page.is_page_load()
        local_storage = niffler.main_page.wd.execute_script('return window.localStorage;')
        token = local_storage['access_token']
        prepare_test_data(token)
        yield niffler
        UserApiHelper(token).remove_all_spending()
        wd.quit()

    @pytest.mark.parametrize('category, expected_length', [
        ('category', 6),
        ('category1', 1),
        ('category2', 2),
        ('category3', 3),
    ])
    def test_search_by_category(self, browser, category: str, expected_length: int):
        browser.main_page.go_to_niffler()

        count_before = browser.main_page.get_count_spending_on_main_page()
        browser.main_page.search_spending(category=category, period='all')
        browser.main_page.wait_while_len_elements_not_equal(MainPage.LIST_SPENDINGS, count_before)
        assert browser.main_page.get_count_spending_on_main_page() == expected_length

    @pytest.mark.parametrize('date_period, expected_length', [
        ('last_month', 7),
        ('today', 6),
    ])
    def test_search_by_date(self, browser, date_period: str, expected_length: int):
        browser.main_page.go_to_niffler()

        count_before = browser.main_page.get_count_spending_on_main_page()
        browser.main_page.search_spending(category='', period=date_period)
        browser.main_page.wait_while_len_elements_not_equal(MainPage.LIST_SPENDINGS, count_before)
        assert browser.main_page.get_count_spending_on_main_page() == expected_length
