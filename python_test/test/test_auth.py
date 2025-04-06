import pytest
from faker import Faker
from selenium import webdriver

from python_test.model.LoginPage import LoginPage
from python_test.model.MainPage import MainPage
from python_test.model.SignUpPage import SignUpPage
from python_test.model.niffler import Niffler

fake = Faker()


class TestPositiveScenario:

    @pytest.fixture(scope="function")
    def browser(self):
        wd = webdriver.Chrome()
        niffler = Niffler(wd)
        yield niffler
        wd.quit()

    def test_login_by_exist_user(self, browser, app_user):
        user_name, password = app_user
        browser.go_to_niffler()
        assert browser.find_element(LoginPage.HEADER).text == 'Log in'

        browser.login_page.login_by_exist_user(user_name, password)
        assert browser.find_element(MainPage.PROFILE_BUTTON).is_displayed(), 'Страница не загрузилась'

    def test_sign_up_gui(self, browser):
        browser.go_sign_up()

        password = fake.password(length=6)
        browser.sign_up_page.fill_user_name(fake.first_name())
        browser.sign_up_page.fill_password(password)
        browser.sign_up_page.fill_password_submit(password)
        browser.sign_up_page.click_sign_up()

        assert browser.find_element(SignUpPage.SUCCESS_NOTIFY).text == "Congratulations! You've registered!"
        assert browser.find_element(SignUpPage.SIGN_IN_BUTTON).is_displayed()


class TestNegativeScenario:

    @pytest.fixture(scope="class")
    def browser(self):
        wd = webdriver.Chrome()
        niffler = Niffler(wd)
        yield niffler
        wd.quit()

    def test_login_by_not_exist_user(self, browser):
        browser.go_to_niffler()
        assert browser.find_element(LoginPage.HEADER).text == 'Log in'

        browser.login_page.fill_user_name(fake.name())
        browser.login_page.fill_password(fake.password(length=5))
        browser.login_page.click_log_in()
        assert browser.find_element(LoginPage.FORM_ERROR_NOTIFY).text == 'Неверные учетные данные пользователя'

    @pytest.mark.parametrize('field_name', ['user', 'password'])
    def test_required_field(self, browser, field_name: str):
        send_text_in_field = {'user': browser.login_page.fill_user_name,
                              'password': browser.login_page.fill_password}
        element = {'user': LoginPage.USER_NAME_FIELD,
                   'password': LoginPage.PASSWORD_FIELD}
        browser.go_to_niffler()
        assert browser.find_element(LoginPage.HEADER).text == 'Log in'

        el = browser.find_element(element[field_name])
        assert el.get_attribute('required')

        send_text_in_field[field_name]('test')
        browser.login_page.click_log_in()
        element_with_message = next((el for el in element.keys() if el != field_name), None)
        assert browser.is_element_have_property(element[element_with_message], 'validationMessage',
                                                'Заполните это поле.')

    @pytest.mark.parametrize('length', (2, 13))
    def test_password_field_boundary_values(self, browser, length: int):
        browser.go_sign_up()
        random_text = fake.lexify(text='?' * length).lower()

        browser.sign_up_page.fill_user_name(fake.first_name())
        browser.sign_up_page.fill_password(random_text)
        browser.sign_up_page.fill_password_submit(random_text)
        browser.sign_up_page.click_sign_up()

        fields_lst = [browser.find_element(e)
                      for e in (SignUpPage.PASSWORD_ERROR_NOTIFY, SignUpPage.PASSWORD_SUBMIT_ERROR_NOTIFY)]
        error_text = 'Allowed password length should be from 3 to 12 characters'
        assert all(el.text == error_text for el in fields_lst), 'Не у каждого поля есть текст предупреждение'

    @pytest.mark.parametrize('length', (2, 51))
    def test_user_field_boundary_values(self, browser, length: int):
        browser.go_sign_up()
        random_text = fake.lexify(text='?' * length).lower()

        browser.sign_up_page.fill_user_name(random_text)
        browser.sign_up_page.fill_password('123')
        browser.sign_up_page.fill_password_submit('123')
        browser.sign_up_page.click_sign_up()

        error_text = 'Allowed username length should be from 3 to 50 characters'
        assert browser.find_element(SignUpPage.USER_ERROR_NOTIFY).text == error_text
