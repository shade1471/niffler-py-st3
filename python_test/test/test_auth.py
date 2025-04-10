from typing import Any, Generator

import pytest
from faker import Faker
from selenium import webdriver

from model.config import Envs
from python_test.model.LoginPage import LoginPage
from python_test.model.niffler import Niffler

fake = Faker()


class TestPositiveScenario:

    @pytest.fixture(scope="function")
    def browser(self) -> Generator[Niffler, Any, None]:
        wd = webdriver.Chrome()
        niffler = Niffler(wd)
        yield niffler
        wd.quit()

    def test_login_by_exist_user(self, browser: Niffler, envs: Envs):
        user_name, password = envs.test_username, envs.test_password
        browser.login_page.go_to_niffler()

        browser.login_page.login_by_exist_user(user_name, password)
        assert browser.main_page.is_page_load(), 'Главная страница не прогрузилась'

    def test_sign_up_gui(self, browser: Niffler):
        browser.sign_up_page.go_sign_up()

        password = fake.password(length=6)
        random_text = fake.lexify(text='?' * 5).lower()
        browser.sign_up_page.fill_user_name(f'{fake.first_name()}{random_text}')
        browser.sign_up_page.fill_password(password)
        browser.sign_up_page.fill_password_submit(password)
        browser.sign_up_page.click_sign_up()

        assert browser.sign_up_page.get_success_sign_up_notify() == "Congratulations! You've registered!"


class TestNegativeScenario:

    @pytest.fixture(scope="class")
    def browser(self) -> Generator[Niffler, Any, None]:
        wd = webdriver.Chrome()
        niffler = Niffler(wd)
        yield niffler
        wd.quit()

    def test_login_by_not_exist_user(self, browser: Niffler):
        browser.login_page.go_to_niffler()
        browser.login_page.fill_user_name(fake.name())
        browser.login_page.fill_password(fake.password(length=5))
        browser.login_page.click_log_in()
        assert browser.login_page.get_text_form_error() == 'Неверные учетные данные пользователя'

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
        assert browser.login_page.is_element_have_property(element[element_with_message], 'validationMessage',
                                                           'Заполните это поле.')

    @pytest.mark.parametrize('length', (2, 13))
    def test_password_field_boundary_values(self, browser: Niffler, length: int):
        browser.sign_up_page.go_sign_up()
        random_text = fake.lexify(text='?' * length).lower()

        browser.sign_up_page.fill_user_name(fake.first_name())
        browser.sign_up_page.fill_password(random_text)
        browser.sign_up_page.fill_password_submit(random_text)
        browser.sign_up_page.click_sign_up()

        fields_lst = browser.sign_up_page.get_notify_list_off_all_fields()
        error_text = 'Allowed password length should be from 3 to 12 characters'
        assert all(el.text == error_text for el in fields_lst), 'Не у каждого поля есть текст предупреждение'

    @pytest.mark.parametrize('length', (2, 51))
    def test_user_field_boundary_values(self, browser: Niffler, length: int):
        browser.sign_up_page.go_sign_up()
        random_text = fake.lexify(text='?' * length).lower()

        browser.sign_up_page.fill_user_name(random_text)
        browser.sign_up_page.fill_password('123')
        browser.sign_up_page.fill_password_submit('123')
        browser.sign_up_page.click_sign_up()

        error_text = 'Allowed username length should be from 3 to 50 characters'
        assert browser.sign_up_page.get_error_text_by_user_field() == error_text
