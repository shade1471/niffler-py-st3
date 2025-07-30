import time
from datetime import datetime, timezone
from http import HTTPStatus

import allure
import pytest
from faker import Faker
from filelock import FileLock
from requests import HTTPError

from python_test.data_helper.api_helper import SpendsHttpClient
from python_test.databases.spend_db import SpendDb
from python_test.fixtures.auth_fixtures import auth_token
from python_test.marks import TestData
from python_test.model.config import Envs
from python_test.model.db.category import Category
from python_test.model.db.spend import SpendAdd
from python_test.report_helper import Epic, Feature, Story


@pytest.fixture(scope="module", autouse=True)
def module_fixture(tmp_path_factory, worker_id, spends_client: SpendsHttpClient, spend_db: SpendDb):
    def _prepare_state():
        categories_ids = spends_client.get_ids_all_categories()
        spend_db.delete_categories_by_ids(categories_ids)
        all_spends_ids = spends_client.get_ids_all_spending()
        for spend_id in all_spends_ids:
            spends_client.delete_spending_by_id(spend_id)

    if worker_id == "master":
        _prepare_state()

    root_tmp_dir = tmp_path_factory.getbasetemp().parent

    fn = root_tmp_dir / "prepare"
    with FileLock(str(fn) + ".lock"):
        if fn.is_file():
            pass
        else:
            _prepare_state()


@pytest.fixture(scope='function', autouse=True)
def wait_before_run_test():
    time.sleep(1)  # Ожидание для отработки фикстуры модуля при параллельном запуске


def get_spend_model(envs: Envs, category_name: str = '') -> dict:
    date = datetime.now(timezone.utc)
    formatted_time = date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    new_spend = {'category': {'name': category_name, 'username': envs.test_username, 'archived': False},
                 'spendDate': formatted_time, 'amount': 100, 'description': '', 'currency': 'RUB',
                 'username': envs.test_username}
    return new_spend

@pytest.mark.parallel
@allure.epic(Epic.niffler)
@allure.feature(Feature.api)
class TestApi:
    @allure.story(Story.api_story['spend'])
    class TestSpend:

        @TestData.spend({
            'category': 'auto',
            'amount': 100_000,
            'currency': 'RUB',
            'desc': 'repair engine',
        })
        @allure.title('Создание новой траты')
        def test_create_spending(self, spends_client: SpendsHttpClient, spend: SpendAdd):
            with allure.step('Проверить наличие созданной траты на корректность данных'):
                new_spend = spends_client.get_spend_by_id(spend.id)
                assert new_spend.amount == spend.amount
                assert new_spend.category.name == spend.category.name
                assert new_spend.currency == spend.currency
                assert new_spend.description == spend.description

        @TestData.spend({
            'category': 'test_get',
            'amount': 100,
            'currency': 'EUR',
            'desc': 'Coursera online courses',
        })
        @allure.title('Получение существующей траты по id')
        def test_get_spend_by_id(self, spends_client: SpendsHttpClient, spend: SpendAdd):
            with allure.step('Получить трату через API по ее id'):
                current_spend = spends_client.get_spend_by_id(spend.id)

            with allure.step('Проверить ответ на корректность данных'):
                assert current_spend.category.name == spend.category.name
                assert current_spend.amount == spend.amount
                assert current_spend.currency == spend.currency
                assert current_spend.description == spend.description

        @TestData.category({'category_name': 'test_amount_required', 'archived': False})
        @allure.title('Обязательность наличия суммы траты')
        def test_required_amount_for_spend(self, envs: Envs, auth_token, category):
            client = SpendsHttpClient(envs, auth_token)
            new_spend = get_spend_model(envs, category.name)
            new_spend.pop('amount')

            with allure.step('Проверить невозможность добавления новой траты по API без суммы'):
                with pytest.raises(HTTPError) as exc_info:
                    client.session.post(url='/api/spends/add', json=new_spend)
                assert exc_info.value.response.status_code == HTTPStatus.BAD_REQUEST

            with allure.step('Проверить ответ, об обязательном наличии поля суммы'):
                body = exc_info.value.response.json()
                assert body['title'] == 'Bad Request'
                assert body['detail'] == 'Amount can not be null'

        @TestData.category({'category_name': 'test_currency_required', 'archived': False})
        @allure.title('Обязательность наличия типа валюты')
        def test_required_currency_for_spend(self, envs: Envs, auth_token, category: Category):
            client = SpendsHttpClient(envs, auth_token)
            new_spend = get_spend_model(envs, category.name)
            new_spend.pop('currency')

            with allure.step('Проверить невозможность добавления новой траты по API без типа валюты'):
                with pytest.raises(HTTPError) as exc_info:
                    client.session.post(url='/api/spends/add', json=new_spend)
                assert exc_info.value.response.status_code == HTTPStatus.BAD_REQUEST

            with allure.step('Проверить ответ, об обязательном наличии поля тип валюты'):
                body = exc_info.value.response.json()
                assert body['title'] == 'Bad Request'
                assert body['detail'] == 'Currency can not be null'

        @allure.title('Обязательность наличия категории в трате')
        def test_required_category_for_spend(self, envs: Envs, auth_token):
            client = SpendsHttpClient(envs, auth_token)
            new_spend = get_spend_model(envs)
            new_spend.pop('category')

            with allure.step('Проверить невозможность добавления новой траты по API без категории'):
                with pytest.raises(HTTPError) as exc_info:
                    client.session.post(url='/api/spends/add', json=new_spend)
                assert exc_info.value.response.status_code == HTTPStatus.BAD_REQUEST

            with allure.step('Проверить ответ, об обязательном наличии категории'):
                body = exc_info.value.response.json()
                assert body['title'] == 'Bad Request'
                assert body['detail'] == 'Category can not be null'

        @TestData.spend({
            'category': 'Food',
            'amount': 30,
            'currency': 'USD',
        })
        @allure.title('Возможность добавления траты без описания')
        def test_add_spend_without_field_desc(self, spends_client: SpendsHttpClient, spend: SpendAdd):
            with allure.step('Проверить ответ, что трата создалась с пустым полем описания'):
                assert spend.description == ''

        @pytest.mark.parametrize('currency', ('RUB', 'USD', 'EUR', 'KZT'))
        @allure.title('Граничные значения для значения суммы')
        def test_amount_boundary_value_for_different_currency(self, envs: Envs, auth_token: str, currency):
            client = SpendsHttpClient(envs, auth_token)
            new_spend = get_spend_model(envs, category_name=currency)
            new_spend['amount'] = 0.009
            new_spend['currency'] = currency

            with allure.step('Попытаться добавить новую трату с суммой меньше 0.01'):
                with pytest.raises(HTTPError) as exc_info:
                    client.session.post(url='/api/spends/add', json=new_spend)
                assert exc_info.value.response.status_code == HTTPStatus.BAD_REQUEST

            with allure.step('Проверить ответ, о минимальном значении суммы'):
                body = exc_info.value.response.json()
                assert body['title'] == 'Bad Request'
                assert body['detail'] == 'Amount should be greater than 0.01'

    @allure.story(Story.api_story['category'])
    class TestCategory:

        @staticmethod
        @allure.step('Создать {count} категории(й)')
        def create_categories(spends_client, count):
            for i in range(1, count + 1):
                spends_client.add_category(f'limit{i}')

        @TestData.category({'category_name': 'test_create_category', 'archived': False})
        @allure.title('Добавление новой категории через API')
        def test_add_category(self, spends_client: SpendsHttpClient, category: Category):
            new_category = spends_client.get_category_by_id(category.id)

            with allure.step('Проверить, что новая категория есть в списке всех категорий'):
                assert category.id in spends_client.get_ids_all_categories()

            with allure.step('Проверить ответ на корректность данных'):
                assert new_category.name == category.name
                assert new_category.archived == category.archived

        @TestData.category({'category_name': 'test_update_category', 'archived': False})
        @allure.title('Обновление существующей категории через API')
        def test_update_category(self, spends_client: SpendsHttpClient, category: Category):
            new_name = 'test_update_name_category'
            new_archived_status = True

            with allure.step('Обновить существующую категорию через API'):
                update_category = spends_client.update_category(category.id, new_name, new_archived_status)

            with allure.step('Проверить, что обновленная категория есть в списке всех категорий'):
                assert category.id in spends_client.get_ids_all_categories()

            with allure.step('Проверить ответ на корректность данных'):
                assert update_category.name == new_name
                assert update_category.archived == new_archived_status

        @TestData.category({'category_name': 'test_duplicate_category', 'archived': False})
        @allure.title('Нет возможности добавить дубль существующей категории')
        def test_no_possible_add_duplicate_category(self, spends_client: SpendsHttpClient, category):
            new_category = {'name': 'test_duplicate_category', 'username': spends_client.user_name, 'archived': False}

            with allure.step('Попытаться добавить дубликат категории'):
                resp = spends_client.session.post('/api/categories/add', json=new_category)
                assert resp.status_code == HTTPStatus.CONFLICT

            with allure.step('Проверить ответ, о невозможности добавления дубликата категории'):
                body = resp.json()
                assert body['title'] == 'Conflict'
                assert body['detail'] == 'Cannot save duplicates'

        @TestData.category({'category_name': 'test_duplicate_archive_category', 'archived': False})
        @allure.title('Нет возможности добавить дубль существующей архивной категории')
        def test_no_possible_add_duplicate_archive_category(self, spends_client: SpendsHttpClient, category):
            new_category = {'name': 'test_duplicate', 'username': spends_client.user_name, 'archived': False}

            with allure.step('Сделать существующую категорию архивной'):
                spends_client.update_category(category.id, new_category['name'], True)

            with allure.step('Попытаться добавить дубликат архивной категории'):
                resp = spends_client.session.post('/api/categories/add', json=new_category)
            assert resp.status_code == HTTPStatus.CONFLICT

            with allure.step('Проверить ответ, о невозможности добавления дубликата архивной категории'):
                body = resp.json()
                assert body['title'] == 'Conflict'
                assert body['detail'] == 'Cannot save duplicates'

        # @allure.title('Максимальное количество не архивных категорий для пользователя')
        # def test_limit_size_categories_for_user(self, spends_client: SpendsHttpClient):
        #     self.create_categories(spends_client, 8)
        #     new_category = {'name': 'category9', 'username': spends_client.user_name, 'archived': False}
        #
        #     with allure.step('Убедиться, что текущее количество не архивных категорий равно 8'):
        #         assert len(spends_client.get_ids_all_categories()) == 8
        #
        #     with allure.step('Попытаться добавить новую категорию'):
        #         resp = spends_client.session.post('/api/categories/add', json=new_category)
        #         assert resp.status_code == HTTPStatus.NOT_ACCEPTABLE
        #
        #     with allure.step('Проверить ответ, о невозможности добавления категории из-за существующего лимита'):
        #         body = resp.json()
        #         assert body['title'] == 'Not Acceptable'
        #         assert 'Can`t add over than 8 categories for user' in body['detail']

        @pytest.mark.parametrize('count', (1, 51))
        @allure.title('Граничные значения по количеству символов в имени категории, negative')
        def test_negative_boundary_values_for_name_category(self, spends_client: SpendsHttpClient,
                                                            count):
            name_category = Faker().lexify(text='?' * count).lower()
            new_category = {'name': name_category, 'username': spends_client.user_name, 'archived': False}

            with allure.step(f'Попытаться добавить новую категории с именем из {count} символов'):
                with pytest.raises(HTTPError) as exc_info:
                    spends_client.session.post('/api/categories/add', json=new_category)
                assert exc_info.value.response.status_code == HTTPStatus.BAD_REQUEST

            with allure.step('Проверить ответ, о допустимом количестве символов в имени категории'):
                body = exc_info.value.response.json()
                assert body['title'] == 'Bad Request'
                assert body['detail'] == 'Allowed category length should be from 2 to 50 characters'

        @pytest.mark.parametrize('count', (2, 50))
        @allure.title('Граничные значения для по количеству символов в имени категории, positive')
        def test_positive_boundary_values_for_name_category(self, spends_client: SpendsHttpClient, count):
            name_category = Faker().lexify(text='?' * count).lower()
            new_category = {'name': name_category, 'username': spends_client.user_name, 'archived': False}

            with allure.step(f'Попытаться добавить новую категории с именем из {count} символов'):
                resp = spends_client.session.post('/api/categories/add', json=new_category)
                assert resp.status_code == HTTPStatus.OK

            with allure.step('Проверить валидность ответа'):
                Category.model_validate(resp.json())
