from selenium.webdriver.common.by import By

from python_test.model.BasePage import BasePage


class SignUpPage:
    HEADER = (By.CSS_SELECTOR, 'h1.header')
    USER_NAME_FIELD = (By.ID, 'username')
    USER_ERROR_NOTIFY = (By.CSS_SELECTOR, 'input[id="username"] + .form__error')
    PASSWORD_FIELD = (By.ID, 'password')
    PASSWORD_ERROR_NOTIFY = (By.CSS_SELECTOR, 'input[id="password"] + button + .form__error')
    PASSWORD_SUBMIT_FIELD = (By.ID, 'passwordSubmit')
    PASSWORD_SUBMIT_ERROR_NOTIFY = (By.CSS_SELECTOR, 'input[id="passwordSubmit"] + button + .form__error')
    SIGN_UP_BUTTON = (By.CSS_SELECTOR, 'button[type="submit"]')
    LINK_TO_LOGIN_PAGE = (By.CSS_SELECTOR, 'a.form__link')
    SUCCESS_NOTIFY = (By.CSS_SELECTOR, 'p.form__paragraph_success')
    SIGN_IN_BUTTON = (By.CSS_SELECTOR, 'a.form_sign-in[href="http://frontend.niffler.dc/main"]')


class SignUpPageHelper(BasePage):

    def fill_user_name(self, name: str):
        el = self.find_element(SignUpPage.USER_NAME_FIELD)
        el.clear()
        el.send_keys(name)

    def fill_password(self, password: str):
        el = self.find_element(SignUpPage.PASSWORD_FIELD)
        el.clear()
        el.send_keys(password)

    def fill_password_submit(self, user_password: str):
        el = self.find_element(SignUpPage.PASSWORD_SUBMIT_FIELD)
        el.clear()
        el.send_keys(user_password)

    def click_sign_up(self):
        self.find_element(SignUpPage.SIGN_UP_BUTTON).click()

    def sign_up_user(self, user_name: str, user_password: str):
        self.fill_user_name(user_name)
        self.fill_password(user_password)
        self.fill_password_submit(user_password)
        self.click_sign_up()
