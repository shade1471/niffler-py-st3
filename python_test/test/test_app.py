from datetime import datetime, timedelta

import pytest

from model.niffler import Niffler
from python_test.data_helper.api_helper import SpendsHttpClient


class TestSpending:

    @pytest.fixture(scope='class')
    def data(self, spends_client: SpendsHttpClient):
        spends_client.remove_all_spending()
        spends_client.add_spend('study', 500)
        yield
        spends_client.remove_all_spending()

    def test_add_spending_gui(self, niffler: Niffler, data):
        niffler.main_page.go_to_niffler()
        count_before = niffler.main_page.get_count_spending_on_main_page()
        niffler.main_page.click_add_spending()
        assert niffler.spending_page.is_page_load()

        niffler.spending_page.add_new_spending(50000, 'study')
        assert niffler.main_page.get_count_spending_on_main_page() == count_before + 1

    def test_required_spending_fields(self, niffler: Niffler):
        niffler.main_page.go_to_niffler()
        niffler.main_page.click_add_spending()
        assert niffler.spending_page.is_page_load()

        niffler.spending_page.click_save()
        assert niffler.spending_page.get_amount_field_helper_text() == 'Amount has to be not less then 0.01'
        assert niffler.spending_page.get_category_field_helper_text() == 'Please choose category'

    def test_add_spending_without_required_category_field(self, niffler: Niffler):
        niffler.main_page.go_to_niffler()
        niffler.main_page.click_add_spending()
        assert niffler.spending_page.is_page_load()

        niffler.spending_page.fill_amount(1000)
        niffler.spending_page.click_save()
        assert niffler.spending_page.get_category_field_helper_text() == 'Please choose category'

    def test_add_spending_without_required_amount_field(self, niffler: Niffler):
        niffler.main_page.go_to_niffler()
        niffler.main_page.click_add_spending()
        assert niffler.spending_page.is_page_load()

        niffler.spending_page.fill_category('study')
        niffler.spending_page.click_save()
        assert niffler.spending_page.get_amount_field_helper_text() == 'Amount has to be not less then 0.01'

    @pytest.mark.parametrize('currency', ('RUB', 'USD', 'EUR', 'KZT'))
    def test_amount_boundary_value_for_different_currency(self, niffler: Niffler, currency: str):
        niffler.main_page.go_to_niffler()
        niffler.main_page.click_add_spending()
        assert niffler.spending_page.is_page_load()

        niffler.spending_page.fill_amount(0.009)
        niffler.spending_page.select_currency(currency)
        niffler.spending_page.fill_category('study')
        niffler.spending_page.click_save()
        assert niffler.spending_page.get_alert_text() == 'Amount should be greater than 0.01'

    def test_delete_spending_gui(self, niffler: Niffler, data, spends_client: SpendsHttpClient):
        spend_id = spends_client.add_spend('study', 500)
        niffler.main_page.go_to_niffler()
        count_before = niffler.main_page.get_count_spending_on_main_page()
        niffler.main_page.delete_spending_by_id(spend_id)

        assert niffler.main_page.get_alert_text() == 'Spendings succesfully deleted'
        assert niffler.main_page.get_count_spending_on_main_page() == count_before - 1


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
    def test_search_by_category(self, niffler: Niffler, data, category: str, expected_length: int):
        niffler.main_page.go_to_niffler()
        count_before = niffler.main_page.get_count_spending_on_main_page()
        niffler.main_page.search_spending(category=category, period='all')
        niffler.main_page.wait_while_counts_spending_not_equal(count_before)
        assert niffler.main_page.get_count_spending_on_main_page() == expected_length

    @pytest.mark.parametrize('date_period, expected_length', [
        ('last_month', 7),
        ('today', 6),
    ])
    def test_search_by_date(self, niffler: Niffler, date_period: str, expected_length: int):
        niffler.main_page.go_to_niffler()
        count_before = niffler.main_page.get_count_spending_on_main_page()

        niffler.main_page.search_spending(category='', period=date_period)
        niffler.main_page.wait_while_counts_spending_not_equal(count_before)
        assert niffler.main_page.get_count_spending_on_main_page() == expected_length

    @pytest.mark.parametrize('currency, expected_length', [
        ('EUR', 1),
        ('USD', 2),
        ('KZT', 3),
        ('RUB', 3),
    ])
    def test_search_by_currency(self, niffler: Niffler, data, currency: str, expected_length: int):
        niffler.main_page.go_to_niffler()
        count_before = niffler.main_page.get_count_spending_on_main_page()

        niffler.main_page.select_currency(currency)
        niffler.main_page.wait_while_counts_spending_not_equal(count_before)
        assert niffler.main_page.get_count_spending_on_main_page() == expected_length
