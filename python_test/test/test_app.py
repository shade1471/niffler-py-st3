from datetime import datetime, timedelta

import allure
import pytest

from python_test.data_helper.api_helper import SpendsHttpClient
from python_test.databases.spend_db import SpendDb
from python_test.marks import TestData
from python_test.model.config import Envs
from python_test.model.db.category import Category
from python_test.model.db.spend import SpendAdd
from python_test.model.niffler import Niffler
from python_test.report_helper import Epic, Feature, Story

pytestmark = [pytest.mark.allure_label(Epic.niffler, label_type="epic")]


@allure.feature(Feature.spending)
class TestSpending:

    @pytest.fixture(scope='class')
    def data(self, spends_client: SpendsHttpClient):
        spends_client.delete_all_spending()
        spends_client.add_spend('study', 2_000)
        yield
        spends_client.delete_all_spending()

    @allure.story(Story.positive_cases)
    @allure.title('Добавление новой траты через GUI Niffler')
    def test_add_spending_gui(self, data, niffler: Niffler):
        niffler.main_page.go_to_niffler()
        count_before = niffler.main_page.get_count_spending_on_main_page()
        niffler.main_page.click_add_spending()
        assert niffler.spending_page.is_page_load()

        niffler.spending_page.add_new_spending(50000, 'study')
        with allure.step('Убедиться в добавлении новой траты на главной странице пользователя'):
            assert niffler.main_page.get_count_spending_on_main_page() == count_before + 1

    @allure.story(Story.negative_cases)
    @allure.title('Подсказки об обязательности полей суммы и категории при добавлении траты')
    def test_required_spending_fields(self, niffler: Niffler):
        niffler.main_page.go_to_niffler()
        niffler.main_page.click_add_spending()
        assert niffler.spending_page.is_page_load()

        niffler.spending_page.click_save()
        with allure.step('Проверить текст предупреждений по полям суммы и категории'):
            assert niffler.spending_page.get_amount_field_helper_text() == 'Amount has to be not less then 0.01'
            assert niffler.spending_page.get_category_field_helper_text() == 'Please choose category'

    @allure.story(Story.negative_cases)
    @allure.title('Создание траты без обязательного поля категории')
    def test_add_spending_without_required_category_field(self, niffler: Niffler):
        niffler.main_page.go_to_niffler()
        niffler.main_page.click_add_spending()
        assert niffler.spending_page.is_page_load()

        niffler.spending_page.fill_amount(1000)
        niffler.spending_page.click_save()

        with allure.step('Проверить текст предупреждения по полю категории'):
            assert niffler.spending_page.get_category_field_helper_text() == 'Please choose category'

    @allure.story(Story.negative_cases)
    @allure.title('Создание траты без обязательного поля суммы')
    def test_add_spending_without_required_amount_field(self, niffler: Niffler):
        niffler.main_page.go_to_niffler()
        niffler.main_page.click_add_spending()
        assert niffler.spending_page.is_page_load()

        niffler.spending_page.fill_category('study')
        niffler.spending_page.click_save()

        with allure.step('Проверить текст предупреждения по полю суммы'):
            assert niffler.spending_page.get_amount_field_helper_text() == 'Amount has to be not less then 0.01'

    @pytest.mark.parametrize('currency', ('RUB', 'USD', 'EUR', 'KZT'))
    @allure.story(Story.negative_cases)
    @allure.title('Создание траты с суммой меньше граничного значения для типа валюты')
    def test_amount_boundary_value_for_different_currency(self, niffler: Niffler, currency: str):
        niffler.main_page.go_to_niffler()
        niffler.main_page.click_add_spending()
        assert niffler.spending_page.is_page_load()

        niffler.spending_page.fill_amount(0.009)
        niffler.spending_page.select_currency(currency)
        niffler.spending_page.fill_category('study')
        niffler.spending_page.click_save()

        with allure.step(f'Проверить текст предупреждения по полю суммы для типа валюты {currency}'):
            assert niffler.spending_page.get_alert_text() == 'Amount should be greater than 0.01'

    @allure.story(Story.positive_cases)
    @allure.title('Удаление траты через GUI Niffler')
    @TestData.spend({'category': 'study', 'amount': 10_000})
    def test_delete_spending_gui(self, niffler: Niffler, data, spend: SpendAdd):
        niffler.main_page.go_to_niffler()
        count_before = niffler.main_page.get_count_spending_on_main_page()
        niffler.main_page.delete_spending_by_id(spend.id)

        with allure.step('Проверить текст алерта после успешного удаления'):
            assert niffler.main_page.get_alert_text() == 'Spendings succesfully deleted'
        with allure.step('Проверить отсутствие траты на главной странице'):
            assert niffler.main_page.get_count_spending_on_main_page() == count_before - 1

    @TestData.spend({
        'category': 'test_db',
        'amount': 10_000,
        'currency': 'KZT',
        'desc': 'Проверка данных из БД',
        'date': datetime(2024, 12, 31)
    })
    @allure.story(Story.api)
    @allure.title('Добавление траты через API, проверка корректности данных в БД')
    def test_data_spend_from_db(self, data, spend: SpendAdd, spend_db: SpendDb, envs: Envs):
        spend_from_db = spend_db.get_spend_by_id(spend_id=spend.id)

        with allure.step('Проверить корректность данных в БД'):
            assert spend_from_db.username == envs.test_username
            assert spend_from_db.amount == spend.amount
            assert spend_from_db.spend_date == datetime.strptime(spend.spendDate, "%Y-%m-%dT%H:%M:%S.%f%z").date()
            assert spend_from_db.currency == spend.currency
            assert spend_from_db.description == spend.description

    @TestData.spend({
        'category': 'study',
        'amount': 600,
        'currency': 'USD',
        'desc': 'Coursera online courses',
        'date': datetime(2024, 10, 10)
    })
    @allure.story(Story.api)
    @allure.title('Обновление траты через API, проверка корректности данных в БД')
    def test_data_spend_from_db_after_api_update(self, data, spend: SpendAdd, spend_db: SpendDb,
                                                 spends_client: SpendsHttpClient):
        new_category = 'Обучение'
        new_amount = 50_000
        new_currency = 'RUB'
        new_desc = 'Онлайн курсы'
        new_date = datetime(2024, 10, 15)

        update_spend = spends_client.update_spend(spend.id, new_category, new_amount, new_currency, new_desc, new_date)

        spend_from_db = spend_db.get_spend_by_id(spend_id=spend.id)
        category_from_db = spend_db.get_category_by_id(update_spend.category.id)

        with allure.step('Проверить корректность данных в БД'):
            assert spend_from_db.id.__str__() == spend.id
            assert category_from_db.name == new_category
            assert spend_from_db.amount == new_amount
            assert spend_from_db.currency == new_currency
            assert spend_from_db.description == new_desc
            assert spend_from_db.spend_date == new_date.date()


@allure.feature(Feature.search)
class TestSearch:

    @pytest.fixture(scope='class')
    def data(self, spends_client: SpendsHttpClient):
        spends_client.delete_all_spending()
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
        spends_client.delete_all_spending()

    @pytest.mark.parametrize('category, expected_length', [
        ('category', 6),
        ('category1', 1),
        ('category2', 2),
        ('category3', 3),
    ])
    @allure.story(Story.search_criteria)
    @allure.title('Поиск трат по имени категории')
    def test_search_by_category(self, niffler: Niffler, data, category: str, expected_length: int):
        niffler.main_page.go_to_niffler()
        count_before = niffler.main_page.get_count_spending_on_main_page()
        niffler.main_page.search_spending(category=category, period='all')
        niffler.main_page.wait_while_counts_spending_not_equal(count_before)

        with allure.step('Проверить количество трат удовлетворяющих критерию'):
            assert niffler.main_page.get_count_spending_on_main_page() == expected_length

    @pytest.mark.parametrize('date_period, expected_length', [
        ('last_month', 7),
        ('today', 6),
    ])
    @allure.story(Story.search_criteria)
    @allure.title('Поиск трат по дате')
    def test_search_by_date(self, niffler: Niffler, date_period: str, expected_length: int):
        niffler.main_page.go_to_niffler()
        count_before = niffler.main_page.get_count_spending_on_main_page()

        niffler.main_page.search_spending(category='', period=date_period)
        niffler.main_page.wait_while_counts_spending_not_equal(count_before)

        with allure.step('Проверить количество трат удовлетворяющих критерию'):
            assert niffler.main_page.get_count_spending_on_main_page() == expected_length

    @pytest.mark.parametrize('currency, expected_length', [
        ('EUR', 1),
        ('USD', 2),
        ('KZT', 3),
        ('RUB', 3),
    ])
    @allure.story(Story.search_criteria)
    @allure.title('Поиск трат по типу валюты')
    def test_search_by_currency(self, niffler: Niffler, data, currency: str, expected_length: int):
        niffler.main_page.go_to_niffler()
        count_before = niffler.main_page.get_count_spending_on_main_page()

        niffler.main_page.select_currency(currency)
        niffler.main_page.wait_while_counts_spending_not_equal(count_before)

        with allure.step('Проверить количество трат удовлетворяющих критерию'):
            assert niffler.main_page.get_count_spending_on_main_page() == expected_length


@allure.feature(Feature.category)
class TestCategory:

    @pytest.fixture()
    def clean_categories(self, spends_client: SpendsHttpClient, spend_db: SpendDb):
        categories_ids = spends_client.get_ids_all_categories()
        spend_db.delete_categories_by_ids(categories_ids)

    @staticmethod
    @allure.step('Создать {count} категории(й)')
    def create_categories(spends_client, count):
        for i in range(1, count + 1):
            spends_client.add_category(f'limit{i}')

    @pytest.mark.parametrize('count, is_not_possible_add', [
        (7, False),
        (8, True)
    ])
    @allure.story(Story.category_restrictions)
    @allure.title('Максимальное количество не архивных категорий для пользователя')
    def test_limit_size_categories_for_user(self, niffler: Niffler, spends_client: SpendsHttpClient, clean_categories,
                                            count: int, is_not_possible_add: bool):
        self.create_categories(spends_client, count)
        niffler.profile_page.open_profile_page()

        with allure.step('Проверить возможность добавления новой категории'):
            assert niffler.profile_page.is_categories_field_disabled() == is_not_possible_add

    @TestData.category({'category_name': 'duplicate', 'archived': False})
    @allure.story(Story.category_restrictions)
    @allure.title('Запрет на дубликаты категорий')
    def test_no_possible_add_duplicate_category(self, clean_categories, niffler: Niffler, category: Category):
        niffler.profile_page.open_profile_page()
        niffler.profile_page.add_category('duplicate')

        with allure.step('Проверить текст алерта'):
            assert 'Cannot save duplicates' in niffler.profile_page.get_text_alert_message()

    @TestData.category({'category_name': 'duplicate_archive', 'archived': False})
    @allure.story(Story.category_restrictions)
    @allure.title('Запрет на дубликаты категорий при существования архивной')
    def test_no_possible_add_dupclicate_when_exist_archive_category(self, clean_categories, niffler: Niffler,
                                                                    category: Category):
        niffler.profile_page.open_profile_page()
        niffler.profile_page.set_archive_category()
        niffler.profile_page.add_category('duplicate_archive')
        niffler.profile_page.wait_error_alert_become_visible()

        with allure.step('Проверить текст алерта'):
            assert 'Cannot save duplicates' in niffler.profile_page.get_text_alert_message()

    @TestData.category({'category_name': 'archive', 'archived': False})
    @allure.story(Story.category_restrictions)
    @allure.title('Архивные категории не отображаются при добавлении траты')
    def test_no_visibility_archived_category_where_add_spending(self, clean_categories, niffler: Niffler,
                                                                spends_client: SpendsHttpClient, category: Category):
        niffler.profile_page.open_profile_page()
        niffler.profile_page.set_archive_category()
        self.create_categories(spends_client, 3)
        niffler.main_page.go_to_niffler()
        niffler.main_page.click_add_spending()
        all_categories = niffler.spending_page.get_all_availability_categories()

        with allure.step('Проверить отсутствие архивной категории в списке'):
            assert category.name not in all_categories

    @TestData.category({'category_name': 'new_category', 'archived': False})
    @allure.story(Story.positive_cases)
    @allure.title('Отображение не архивной категории пользователя при добавлении траты')
    def test_visibility_exist_category_where_add_spending(self, clean_categories, niffler: Niffler, category: Category):
        niffler.main_page.go_to_niffler()
        niffler.main_page.click_add_spending()
        all_categories = niffler.spending_page.get_all_availability_categories()

        with allure.step('Проверить наличие категории в списке'):
            assert category.name in all_categories

    @TestData.category({
        'category_name': 'test_db',
        'archived': False,
    })
    @allure.story(Story.api)
    @allure.title('Добавление категории через API, проверка корректности данных в БД')
    def test_data_category_from_db(self, clean_categories, category: Category, spend_db: SpendDb, envs: Envs):
        category_from_db = spend_db.get_category_by_id(category_id=category.id)

        with allure.step('Проверить корректность данных в БД'):
            assert category_from_db.archived == category.archived
            assert category_from_db.name == category.name
            assert category_from_db.username == envs.test_username

    @TestData.category({
        'category_name': 'category_db_after_update',
        'archived': False,
    })
    @allure.story(Story.api)
    @allure.title('Обновление категории через API, проверка корректности данных в БД')
    def test_data_category_from_db_after_api_update(self, clean_categories, category: Category, spend_db: SpendDb,
                                                    spends_client: SpendsHttpClient):
        new_category_name = 'api_update_category'
        new_attribute_archived = True

        spends_client.update_category(category.id, new_category_name, new_attribute_archived)
        category_from_db = spend_db.get_category_by_id(category_id=category.id)

        with allure.step('Проверить корректность данных в БД'):
            assert category_from_db.name == new_category_name
            assert category_from_db.archived == new_attribute_archived
