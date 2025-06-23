from typing import Any, Generator

import allure
import pytest
from faker import Faker
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from python_test.model.LoginPage import LoginPage
from python_test.model.config import Envs
from python_test.model.niffler import Niffler
from python_test.report_helper import Epic, Feature, Story

fake = Faker()

pytestmark = [pytest.mark.allure_label(Epic.niffler, label_type="epic")]


@allure.story(Story.positive_cases)
class TestPositiveScenario:

    @pytest.fixture(scope="function")
    def browser(self) -> Generator[Niffler, Any, None]:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--incognito")
        options.add_argument("--disable-dev-shm-usage")
        wd = webdriver.Chrome(options=options)
        niffler = Niffler(wd)
        yield niffler
        wd.quit()

    @allure.feature(Feature.log_in)
    @allure.title('Авторизация под существующим пользователем')
    def test_login_by_exist_user(self, envs: Envs, browser: Niffler):
        user_name, password = envs.test_username, envs.test_password
        browser.login_page.go_to_niffler()

        browser.login_page.login_by_exist_user(user_name, password)
        with allure.step('Проверить загрузку главной страницы пользователя'):
            assert browser.main_page.is_page_load(), 'Главная страница не прогрузилась'

    @allure.feature(Feature.sign_up)
    @allure.title('Регистрация пользователя с валидными данными')
    def test_sign_up_gui(self, browser: Niffler):
        browser.sign_up_page.go_sign_up()

        password = fake.password(length=6)
        random_text = fake.lexify(text='?' * 5).lower()
        browser.sign_up_page.fill_user_name(f'{fake.first_name()}{random_text}')
        browser.sign_up_page.fill_password(password)
        browser.sign_up_page.fill_password_submit(password)
        browser.sign_up_page.click_sign_up()

        with allure.step('Проверить текст уведомления об успешной регистрации'):
            assert browser.sign_up_page.get_success_sign_up_notify() == "Congratulations! You've registered!"


@allure.story(Story.negative_cases)
class TestNegativeScenario:

    @pytest.fixture(scope="class")
    def browser(self) -> Generator[Niffler, Any, None]:
        options = Options()
        options.add_argument("--lang=ru-ru")
        options.add_argument("--headless")
        options.add_argument("--incognito")
        options.add_argument("--disable-dev-shm-usage")
        wd = webdriver.Chrome(options=options)
        niffler = Niffler(wd)
        yield niffler
        wd.quit()

    @allure.feature(Feature.log_in)
    @allure.title('Авторизация под не существующим пользователем')
    def test_login_by_not_exist_user(self, browser: Niffler):
        browser.login_page.go_to_niffler()
        browser.login_page.fill_user_name(fake.name())
        browser.login_page.fill_password(fake.password(length=5))
        browser.login_page.click_log_in()

        with allure.step('Проверить текст сообщения'):
            assert browser.login_page.get_text_form_error() == 'Неверные учетные данные пользователя'

    @allure.feature(Feature.log_in)
    @allure.title('Наличие свойства required у полей имя пользователя и пароль')
    @pytest.mark.parametrize('field_name', ['user', 'password'])
    def test_required_field(self, browser: Niffler, field_name: str):
        send_text_in_field = {'user': browser.login_page.fill_user_name, 'password': browser.login_page.fill_password}
        element = {'user': LoginPage.USER_NAME_FIELD, 'password': LoginPage.PASSWORD_FIELD}
        browser.login_page.go_to_niffler()

        el = browser.login_page.find_element(element[field_name])
        assert el.get_attribute('required')

        send_text_in_field[field_name]('test')
        browser.login_page.click_log_in()
        element_with_message = next((el for el in element.keys() if el != field_name), None)

        with allure.step('Проверить текст о незаполненности поля'):
            assert browser.login_page.is_element_have_property(element[element_with_message], 'validationMessage',
                                                               'Заполните это поле.')

    @allure.feature(Feature.sign_up)
    @allure.title('Граничные значения у поля "Пароль" на странице регистрации')
    @pytest.mark.parametrize('length', (2, 13))
    def test_password_field_boundary_values(self, browser: Niffler, length: int):
        browser.sign_up_page.go_sign_up()
        random_text = fake.lexify(text='?' * length).lower()

        browser.sign_up_page.fill_user_name(fake.first_name())
        browser.sign_up_page.fill_password(random_text)
        browser.sign_up_page.fill_password_submit(random_text)
        browser.sign_up_page.click_sign_up()

        fields_lst = browser.sign_up_page.get_notify_list_off_all_fields()

        with allure.step('Проверить текст предупреждения о min/max количестве символов у пароля'):
            error_text = 'Allowed password length should be from 3 to 12 characters'
            assert all(el.text == error_text for el in fields_lst), 'Не у каждого поля есть текст предупреждение'

    @allure.feature(Feature.sign_up)
    @allure.title('Граничные значения у поля "Имя пользователя" на странице регистрации')
    @pytest.mark.parametrize('length', (2, 51))
    def test_user_field_boundary_values(self, browser: Niffler, length: int):
        browser.sign_up_page.go_sign_up()
        random_text = fake.lexify(text='?' * length).lower()

        browser.sign_up_page.fill_user_name(random_text)
        browser.sign_up_page.fill_password('123')
        browser.sign_up_page.fill_password_submit('123')
        browser.sign_up_page.click_sign_up()

        with allure.step('Проверить текст предупреждения о min/max количестве символов по имени пользователя'):
            error_text = 'Allowed username length should be from 3 to 50 characters'
            assert browser.sign_up_page.get_error_text_by_user_field() == error_text
