import allure
from selenium.webdriver.common.by import By

from python_test.model.BasePage import BasePage


class SignUpPage(BasePage):
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

    def is_page_load(self):
        return self.find_element(self.SIGN_UP_BUTTON).is_displayed()

    @allure.step('Перейти на страницу регистрации Niffler')
    def go_sign_up(self):
        self.wd.get(self.sign_up_url)
        assert self.is_page_load(), 'Страница регистрации не прогрузилась'

    @allure.step('Заполнить поле "Имя пользователя"')
    def fill_user_name(self, name: str):
        el = self.find_element(self.USER_NAME_FIELD)
        el.clear()
        el.send_keys(name)

    @allure.step('Заполнить поле "Пароль"')
    def fill_password(self, password: str):
        el = self.find_element(self.PASSWORD_FIELD)
        el.clear()
        el.send_keys(password)

    @allure.step('Заполнить поле "Подтверждение пароля"')
    def fill_password_submit(self, user_password: str):
        el = self.find_element(self.PASSWORD_SUBMIT_FIELD)
        el.clear()
        el.send_keys(user_password)

    @allure.step('Нажать кнопку "Sign UP"')
    def click_sign_up(self):
        self.find_element(self.SIGN_UP_BUTTON).click()

    @allure.step('Зарегистрировать пользователя {user_name}')
    def sign_up_user(self, user_name: str, user_password: str):
        self.fill_user_name(user_name)
        self.fill_password(user_password)
        self.fill_password_submit(user_password)
        self.click_sign_up()

    def get_success_sign_up_notify(self):
        return self.find_element(self.SUCCESS_NOTIFY).text

    @allure.step('Получить текст ошибки у поля "Имя пользователя"')
    def get_error_text_by_user_field(self):
        return self.find_element(self.USER_ERROR_NOTIFY).text

    def get_notify_list_off_all_fields(self):
        return [self.find_element(e) for e in (self.PASSWORD_ERROR_NOTIFY, self.PASSWORD_SUBMIT_ERROR_NOTIFY)]
