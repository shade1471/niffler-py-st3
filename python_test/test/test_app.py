import logging
from datetime import datetime, timedelta

import pytest
from selenium import webdriver

from python_test.data_helper.api_helper import SpendsHttpClient
from python_test.model.MainPage import MainPage
from python_test.model.SpendingPage import SpendingPage
from python_test.model.niffler import Niffler


@pytest.fixture(scope="module")
def browser(auth):
    niffler, _, _ = auth
    yield niffler
    niffler.wd.quit()


class TestSpending:

    @pytest.fixture(scope='class')
    def data(self, spends_client: SpendsHttpClient):
        spends_client.remove_all_spending()
        spends_client.add_spend('study', 500)
        yield
        spends_client.remove_all_spending()

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

    def test_add_spending_without_required_amount_field(self, browser):
        browser.main_page.go_to_niffler()
        browser.main_page.click_add_spending()
        browser.spending_page.fill_amount(1000)
        browser.spending_page.click_save()
        assert browser.spending_page.get_category_field_helper_text() == 'Please choose category'

    def test_add_spending_without_required_category_field(self, browser):
        browser.go_to_niffler()
        browser.main_page.click_add_spending()
        browser.spending_page.fill_category('study')
        browser.spending_page.click_save()
        assert browser.find_element(SpendingPage.AMOUNT_HELPER_TEXT).text == 'Amount has to be not less then 0.01'

    @pytest.mark.parametrize('currency', ('RUB', 'USD', 'EUR', 'KZT'))
    def test_amount_boundary_value_for_different_currency(self, browser, currency):
        browser.go_to_niffler()
        browser.main_page.click_add_spending()
        browser.spending_page.fill_amount(0.009)
        browser.spending_page.select_currency(currency)
        browser.spending_page.fill_category('study')
        browser.spending_page.click_save()
        assert browser.find_element(SpendingPage.ALERT).text == 'Amount should be greater than 0.01'

    def test_delete_spending_gui(self, browser, data, spends_client: SpendsHttpClient):
        spend_id = spends_client.add_spend('study', 500)
        browser.go_to_niffler()
        count_before = len(browser.find_elements(MainPage.LIST_SPENDINGS))
        browser.main_page.delete_spending_by_id(spend_id)

        alert = browser.find_element(MainPage.ALERT)
        assert alert.is_displayed()
        assert alert.text == 'Spendings succesfully deleted'
        assert len(browser.find_elements(MainPage.LIST_SPENDINGS)) == count_before - 1


class TestSearch:

    @pytest.fixture(scope='class')
    def data(self, spends_client: SpendsHttpClient):
        spends_client.remove_all_spending()
        spends_client.add_spend('category1', 10000, currency='KZT')
        spends_client.add_spend('category2', 1000, currency='EUR')
        spends_client.add_spend('category2', 1000, currency='USD')
        spends_client.add_spend('category3', 50, currency='USD')
        spends_client.add_spend('category3', 1000, currency='KZT')
        spends_client.add_spend('category3', 4000, currency='KZT')
        spends_client.add_spend('past spending', 300, date=datetime(2020, 12, 31))
        spends_client.add_spend('past spending', 700, date=datetime(2021, 1, 1))
        spends_client.add_spend('past spending', 700, date=datetime.now() - timedelta(days=9))
        yield
        spends_client.remove_all_spending()

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

    def test_search_by_category(self, browser, data, category: str, expected_length: int):
        browser.go_to_niffler()
        assert browser.find_element(MainPage.PROFILE_BUTTON).is_displayed()

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
        assert browser.find_element(MainPage.PROFILE_BUTTON).is_displayed()

        count_before = browser.main_page.get_count_spending_on_main_page()
        browser.main_page.search_spending(category='', period=date_period)
        browser.main_page.wait_while_len_elements_not_equal(MainPage.LIST_SPENDINGS, count_before)
        assert browser.main_page.get_count_spending_on_main_page() == expected_length

    @pytest.mark.parametrize('currency, expected_length', [
        ('EUR', 1),
        ('USD', 2),
        ('KZT', 3),
        ('RUB', 3),
    ])
    def test_search_by_currency(self, browser, data, currency: str, expected_length: int):
        browser.go_to_niffler()
        assert browser.find_element(MainPage.PROFILE_BUTTON).is_displayed()

        count_before = len(browser.find_elements(MainPage.LIST_SPENDINGS))
        browser.main_page.select_currency(currency)
        browser.wait_while_len_elements_not_equal(MainPage.LIST_SPENDINGS, count_before)
        assert browser.is_element_have_property(MainPage.TABLE_SPENDINGS, 'childElementCount', value=expected_length)
