from selenium.webdriver.common.by import By

from python_test.model.BasePage import BasePage
from python_test.model.MainPage import MainPage


class LoginPage:
    HEADER = (By.CSS_SELECTOR, 'h1.header')
    USER_NAME_FIELD = (By.NAME, 'username')
    PASSWORD_FIELD = (By.NAME, 'password')
    LOG_IN_BUTTON = (By.CSS_SELECTOR, '.form__submit[type="submit"]')
    CREATE_NEW_ACCOUNT_BUTTON = (By.CSS_SELECTOR, 'a[href="/register"]')
    FORM_ERROR_NOTIFY = (By.CSS_SELECTOR, '.form__error')


class LoginPageHelper(BasePage):

    def fill_user_name(self, user_name: str):
        el = self.find_element(LoginPage.USER_NAME_FIELD)
        el.clear()
        el.send_keys(user_name)

    def fill_password(self, password: str):
        el = self.find_element(LoginPage.PASSWORD_FIELD)
        el.clear()
        el.send_keys(password)

    def click_log_in(self):
        self.find_element(LoginPage.LOG_IN_BUTTON).click()

    def login_by_exist_user(self, user_name: str, password: str):
        self.fill_user_name(user_name)
        self.fill_password(password)
        self.click_log_in()
        assert self.find_element(MainPage.PROFILE_BUTTON).is_displayed()
