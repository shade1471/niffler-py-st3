from datetime import datetime
from typing import Literal

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from python_test.model.BasePage import BasePage
from python_test.model.SpendingPage import SpendingPage


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
    DELETE_BUTTON = (By.ID, 'delete')
    SELECT_ALL_CATEGORY = (By.CSS_SELECTOR, '[data-testid="CheckBoxOutlineBlankIcon"]')
    LIST_SPENDINGS = (By.CSS_SELECTOR, 'tr[role="checkbox"]')
    TABLE_SPENDINGS = (By.CSS_SELECTOR, 'table tbody')

    def is_page_load(self):
        return self.find_element(self.PROFILE_BUTTON).is_displayed()

    def go_to_niffler(self):
        self.wd.get(self.base_url)
        assert self.is_page_load(), 'Главная страница не прогрузилась'

    def click_add_spending(self):
        self.find_element(self.NEW_SPENDING_BUTTON).click()

    def add_new_spending(self, amount: int, category: str, date: datetime = None, desc: str = None):
        self.click_add_spending()

        spending_page = SpendingPage(self.wd)
        spending_page.fill_amount(amount)
        spending_page.fill_category(category)
        if date:
            spending_page.fill_date(date)
        if desc:
            spending_page.fill_description(desc)
        spending_page.click_save()

    def fill_search_field(self, value: str):
        el = self.find_element(self.SEARCH_INPUT)
        el.clear()
        el.send_keys(value)

    def run_search(self):
        self.find_element(self.SEARCH_INPUT).send_keys(Keys.RETURN)

    def select_date(self, date_period: Literal['all', 'last_month', 'last_week', 'today']):
        el_dict = {'all': self.PERIOD_ALL, 'last_month': self.PERIOD_MONTH,
                   'last_week': self.PERIOD_WEEK, 'today': self.PERIOD_TODAY}
        if date_period not in ('all', 'last_month', 'last_week', 'today'):
            raise ValueError('Не правильно указан фильтр по дате')
        self.find_element(self.PERIOD_SELECTOR).click()
        self.find_element(el_dict[date_period]).click()

    def select_currency(self, currency: str):
        pass

    def search_spending(self, category: str, period: Literal['all', 'last_month', 'last_week', 'today']):
        self.select_date(period)
        self.fill_search_field(category)
        self.run_search()

    def get_count_spending_on_main_page(self) -> int:
        return self.get_element_property(self.TABLE_SPENDINGS, 'childElementCount')
