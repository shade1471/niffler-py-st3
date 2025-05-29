import allure
from selenium.webdriver.common.by import By

from python_test.model.BasePage import BasePage


class LoginPage(BasePage):
    HEADER = (By.CSS_SELECTOR, 'h1.header')
    USER_NAME_FIELD = (By.NAME, 'username')
    PASSWORD_FIELD = (By.NAME, 'password')
    LOG_IN_BUTTON = (By.CSS_SELECTOR, '.form__submit[type="submit"]')
    CREATE_NEW_ACCOUNT_BUTTON = (By.CSS_SELECTOR, 'a[href="/register"]')
    FORM_ERROR_NOTIFY = (By.CSS_SELECTOR, '.form__error')

    def is_page_load(self):
        return self.find_element(self.LOG_IN_BUTTON).is_displayed(), 'Страница авторизации не прогрузилась'

    @allure.step('Перейти на страницу авторизации Niffler')
    def go_to_niffler(self):
        self.wd.get(self.base_url)
        assert self.is_page_load(), 'Страница авторизации не прогрузилась'

    @allure.step('Заполнить поле "Имя пользователя"')
    def fill_user_name(self, user_name: str):
        el = self.find_element(self.USER_NAME_FIELD)
        el.clear()
        el.send_keys(user_name)

    @allure.step('Заполнить поле "Пароль"')
    def fill_password(self, password: str):
        el = self.find_element(self.PASSWORD_FIELD)
        el.clear()
        el.send_keys(password)

    @allure.step('Нажать кнопку "Log In"')
    def click_log_in(self):
        self.find_element(self.LOG_IN_BUTTON).click()

    @allure.step('Авторизоваться под пользователем')
    def login_by_exist_user(self, user_name: str, password: str):
        self.fill_user_name(user_name)
        self.fill_password(password)
        self.click_log_in()

    @allure.step('Получить текст ошибки формы')
    def get_text_form_error(self):
        return self.find_element(self.FORM_ERROR_NOTIFY).text
