from selenium.webdriver.common.by import By

from python_test.model.BasePage import BasePage


class SignUpPage:
    HEADER = (By.CSS_SELECTOR, 'h1.header')
    USER_NAME_FIELD = (By.ID, 'username')
    PASSWORD_FIELD = (By.ID, 'passwordSubmit')
    SIGN_UP_BUTTON = (By.CSS_SELECTOR, '[type="submit"]')
    LINK_TO_LOGIN_PAGE = (By.CSS_SELECTOR, 'a.form__link')
    FORM_ERROR_NOTIFY = (By.CSS_SELECTOR, '.form__error')

class LoginPageHelper(BasePage):

    def fill_user_name(self, name):
        self.find_element(SignUpPage.USER_NAME_FIELD).send_keys(name)

    def fill_password(self, password):
        self.find_element(SignUpPage.PASSWORD_FIELD).send_keys(password)

    def login_by_user(self, user_name, password):
        pass