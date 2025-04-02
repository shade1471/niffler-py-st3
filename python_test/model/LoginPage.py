import time

from selenium.webdriver.common.by import By

from python_test.model.BasePage import BasePage


class LoginPage:
    HEADER = (By.CSS_SELECTOR, 'h1.header')
    USER_NAME_FIELD = (By.NAME, 'username')
    PASSWORD_FIELD = (By.NAME, 'password')
    LOG_IN_BUTTON = (By.CSS_SELECTOR, '.form__submit[type="submit"]')
    CREATE_NEW_ACCOUNT_BUTTON = (By.CSS_SELECTOR, 'a[href="/register"]')

class LoginPageHelper(BasePage):

    def fill_user_name(self, name):
        self.find_element(LoginPage.USER_NAME_FIELD).send_keys(name)

    def fill_password(self, password):
        self.find_element(LoginPage.PASSWORD_FIELD).send_keys(password)

    def login_by_user(self, user_name, password):
        self.fill_user_name(user_name)
        self.fill_password(password)
        self.find_element(LoginPage.LOG_IN_BUTTON).click()