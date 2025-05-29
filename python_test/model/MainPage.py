from typing import Literal

import allure
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from python_test.model.BasePage import BasePage


class MainPage(BasePage):
    PROFILE_BUTTON = (By.CSS_SELECTOR, '[aria-label="Menu"]')
    NEW_SPENDING_BUTTON = (By.CSS_SELECTOR, 'a[href="/spending"]')
    SEARCH_INPUT = (By.CSS_SELECTOR, 'input[aria-label="search"]')
    SEARCH_BUTTON = (By.ID, 'input-submit')
    PERIOD_SELECTOR = (By.CSS_SELECTOR, 'div[id="spendings"] .MuiToolbar-root div.MuiBox-root div')
    PERIOD_ALL = (By.CSS_SELECTOR, 'li[data-value="ALL"]')
    PERIOD_MONTH = (By.CSS_SELECTOR, 'li[data-value="MONTH"]')
    PERIOD_WEEK = (By.CSS_SELECTOR, 'li[data-value="WEEK"]')
    PERIOD_TODAY = (By.CSS_SELECTOR, 'li[data-value="TODAY"]')
    CURRENCY_SELECTOR = (By.CSS_SELECTOR, 'div[id="spendings"] .MuiToolbar-root div.MuiBox-root div + div')
    CURRENCY_ALL = (By.CSS_SELECTOR, 'li[data-value="ALL"]')
    CURRENCY_RUB = (By.CSS_SELECTOR, 'li[data-value="RUB"]')
    CURRENCY_USD = (By.CSS_SELECTOR, 'li[data-value="USD"]')
    CURRENCY_KZT = (By.CSS_SELECTOR, 'li[data-value="KZT"]')
    CURRENCY_EUR = (By.CSS_SELECTOR, 'li[data-value="EUR"]')
    DELETE_BUTTON = (By.ID, 'delete')
    SUBMIT_DELETE_BUTTON = (By.CSS_SELECTOR, '[aria-describedby="alert-dialog-slide-description"] button + button')
    SELECT_ALL_CATEGORY = (By.CSS_SELECTOR, '[data-testid="CheckBoxOutlineBlankIcon"]')
    LIST_SPENDINGS = (By.CSS_SELECTOR, 'tr[role="checkbox"]')
    TABLE_SPENDINGS = (By.CSS_SELECTOR, 'table tbody')
    EDIT_SPENDINS = (By.CSS_SELECTOR, '[aria-label="Edit spending"]')
    ALERT = (By.CSS_SELECTOR, '[role="alert"]')

    def is_page_load(self):
        return self.wait_element_becomes_visible(self.PROFILE_BUTTON)

    @allure.step('Перейти на главную страницу Niffler')
    def go_to_niffler(self):
        self.wd.get(self.base_url)
        assert self.is_page_load(), 'Главная страница не прогрузилась'

    @allure.step('Нажать кнопку "Добавить трату"')
    def click_add_spending(self):
        self.find_element(self.NEW_SPENDING_BUTTON).click()

    @allure.step('Заполнить поле поиска')
    def fill_search_field(self, value: str):
        el = self.find_element(self.SEARCH_INPUT)
        el.clear()
        el.send_keys(value)

    @allure.step('Выполнить поиск')
    def run_search(self):
        self.find_element(self.SEARCH_INPUT).send_keys(Keys.RETURN)

    @allure.step('Выбрать дату')
    def select_date(self, date_period: Literal['all', 'last_month', 'last_week', 'today']):
        el_dict = {'all': self.PERIOD_ALL, 'last_month': self.PERIOD_MONTH,
                   'last_week': self.PERIOD_WEEK, 'today': self.PERIOD_TODAY}
        if date_period not in ('all', 'last_month', 'last_week', 'today'):
            raise ValueError('Не правильно указан фильтр по дате')
        self.find_element(self.PERIOD_SELECTOR).click()
        self.find_element(el_dict[date_period]).click()

    @allure.step('Выбрать тип валюты')
    def select_currency(self, currency: Literal['RUB', 'USD', 'EUR', 'KZT']):
        currency_locator = {'RUB': self.CURRENCY_RUB, 'USD': self.CURRENCY_USD,
                            'KZT': self.CURRENCY_KZT, 'EUR': self.CURRENCY_EUR}
        self.find_element(self.CURRENCY_SELECTOR).click()
        self.find_element(currency_locator[currency]).click()

    @allure.step('Выполнить поиск по заданным критериям')
    def search_spending(self, category: str, period: Literal['all', 'last_month', 'last_week', 'today']):
        self.select_date(period)
        self.fill_search_field(category)
        self.run_search()

    @allure.step('Получить количество трат на главной странице')
    def get_count_spending_on_main_page(self) -> int:
        return self.get_element_property(self.TABLE_SPENDINGS, 'childElementCount')

    @allure.step('Удалить трату через GUI')
    def delete_spending_by_id(self, id_spending: str):
        self.find_element((By.CSS_SELECTOR, f'input[aria-labelledby="enhanced-table-checkbox-{id_spending}"]')).click()
        self.find_element(self.DELETE_BUTTON).click()
        self.wait_element_to_be_clickable(self.SUBMIT_DELETE_BUTTON).click()

    def wait_while_counts_spending_not_equal(self, value: int, timeout=10):
        self.wait_while_len_elements_not_equal(self.LIST_SPENDINGS, value, timeout)

    @allure.step('Получить текст алерта')
    def get_alert_text(self) -> str:
        alert = self.find_element(self.ALERT)
        return alert.text

    @allure.step('Кликнуть по профилю пользователя')
    def open_user_profile(self):
        self.find_element(MainPage.PROFILE_BUTTON).click()
