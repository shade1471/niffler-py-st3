from datetime import datetime, timedelta

import pytest
from faker import Faker

from model.ProfilePage import ProfilePage
from python_test.data_helper.api_helper import SpendsHttpClient
from python_test.model.MainPage import MainPage
from python_test.model.SpendingPage import SpendingPage

fake = Faker()


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

    def test_add_spending_gui(self, browser, data):
        browser.go_to_niffler()
        count_before = len(browser.find_elements(MainPage.LIST_SPENDINGS))
        browser.main_page.add_new_spending(50000, 'study')
        assert len(browser.find_elements(MainPage.LIST_SPENDINGS)) == count_before + 1

    def test_required_spending_fields(self, browser):
        browser.go_to_niffler()
        browser.main_page.click_add_spending()
        browser.spending_page.click_save()
        assert browser.find_element(SpendingPage.AMOUNT_HELPER_TEXT).text == 'Amount has to be not less then 0.01'
        assert browser.find_element(SpendingPage.CATEGORY_HELPER_TEXT).text == 'Please choose category'

    def test_add_spending_without_required_amount_field(self, browser):
        browser.go_to_niffler()
        browser.main_page.click_add_spending()
        browser.spending_page.fill_amount(1000)
        browser.spending_page.click_save()
        assert browser.find_element(SpendingPage.CATEGORY_HELPER_TEXT).text == 'Please choose category'

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


class TestCategory:

    @pytest.fixture()
    def data_limit(self, spends_client, spend_db):
        categories_ids = spends_client.get_ids_all_categories()
        for category_id in categories_ids:
            spend_db.delete_category(category_id)
        new_categories = []
        for i in range(1, 9):
            category_id = spends_client.add_category(f'limit{i}').id
            new_categories.append(category_id)
        yield
        for category_id in new_categories:
            spend_db.delete_category(category_id)

    @pytest.fixture()
    def data(self, spends_client, spend_db):
        categories_ids = spends_client.get_ids_all_categories()
        for category_id in categories_ids:
            spend_db.delete_category(category_id)
        category_id = spends_client.add_category('duplicate', archived=True).id
        yield
        spend_db.delete_category(category_id)

    @pytest.fixture()
    def data1(self, spends_client, spend_db):
        categories_ids = spends_client.get_ids_all_categories()
        for category_id in categories_ids:
            spend_db.delete_category(category_id)
        category_id = spends_client.add_category('duplicate').id
        yield
        spend_db.delete_category(category_id)

    def test_max_size_categories_for_user(self, browser, data_limit):
        browser.open_profile_page()
        category_field = browser.main_page.find_element(ProfilePage.CATEGORY_FIELD)
        error_el = browser.main_page.find_element(ProfilePage.CATEGORY_FIELD_ERROR)
        assert category_field.get_attribute('disabled')
        assert error_el.get_attribute('aria-label') == "You've reached maximum available count of active categories"

    def test_no_possible_add_dupclicate_archived_category(self, browser, spends_client, spend_db, data):
        browser.open_profile_page()
        browser.profile_page.add_category('duplicate')
        alert = browser.profile_page.find_element(ProfilePage.ALERT_MESSAGE)
        assert alert.text == 'Error while adding category duplicate: Cannot save duplicates'

    def test_no_possible_add_dupclicate_category(self, browser, spends_client, spend_db, data1):
        browser.open_profile_page()
        browser.profile_page.add_category('duplicate')
        alert = browser.profile_page.find_element(ProfilePage.ALERT_MESSAGE)
        assert alert.text == 'Error while adding category duplicate: Cannot save duplicates'


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

    @pytest.mark.parametrize('category, expected_length', [
        ('category', 6),
        ('category1', 1),
        ('category2', 2),
        ('category3', 3),
    ])
    def test_search_by_category(self, browser, data, category: str, expected_length: int):
        browser.go_to_niffler()
        assert browser.find_element(MainPage.PROFILE_BUTTON).is_displayed()

        count_before = len(browser.find_elements(MainPage.LIST_SPENDINGS))
        browser.main_page.search_spending(category=category, period='all')
        browser.wait_while_len_elements_not_equal(MainPage.LIST_SPENDINGS, count_before)
        assert browser.is_element_have_property(MainPage.TABLE_SPENDINGS, 'childElementCount', value=expected_length)

    @pytest.mark.parametrize('date_period, expected_length', [
        ('last_month', 7),
        ('today', 6),
    ])
    def test_search_by_date(self, browser, data, date_period: str, expected_length: int):
        browser.go_to_niffler()
        assert browser.find_element(MainPage.PROFILE_BUTTON).is_displayed()

        count_before = len(browser.find_elements(MainPage.LIST_SPENDINGS))
        browser.main_page.search_spending(category='', period=date_period)
        browser.wait_while_len_elements_not_equal(MainPage.LIST_SPENDINGS, count_before)
        assert browser.is_element_have_property(MainPage.TABLE_SPENDINGS, 'childElementCount', value=expected_length)

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
