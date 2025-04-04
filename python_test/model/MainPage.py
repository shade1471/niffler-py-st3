from datetime import datetime
from typing import Literal

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from python_test.model.BasePage import BasePage
from python_test.model.SpendingPage import SpendingPageHelper


class MainPage:
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


class MainPageHelper(BasePage):

    def click_add_spending(self):
        self.find_element(MainPage.NEW_SPENDING_BUTTON).click()

    def add_new_spending(self, amount: int, category: str, date: datetime = None, desc: str = None):
        self.click_add_spending()

        spending_page = SpendingPageHelper(self.wd)
        spending_page.fill_amount(amount)
        spending_page.fill_category(category)
        if date:
            spending_page.fill_date(date)
        if desc:
            spending_page.fill_description(desc)
        spending_page.click_save()

    def fill_search_field(self, value: str):
        el = self.find_element(MainPage.SEARCH_INPUT)
        el.clear()
        el.send_keys(value)

    def run_search(self):
        self.find_element(MainPage.SEARCH_INPUT).send_keys(Keys.RETURN)

    def select_date(self, date_period: Literal['all', 'last_month', 'last_week', 'today']):
        el_dict = {'all': MainPage.PERIOD_ALL, 'last_month': MainPage.PERIOD_MONTH,
                   'last_week': MainPage.PERIOD_WEEK, 'today': MainPage.PERIOD_TODAY}
        if date_period not in ('all', 'last_month', 'last_week', 'today'):
            raise ValueError('Не правильно указан фильтр по дате')
        self.find_element(MainPage.PERIOD_SELECTOR).click()
        self.find_element(el_dict[date_period]).click()

    def select_currency(self, currency: str):
        pass

    def search_spending(self, category: str, period: Literal['all', 'last_month', 'last_week', 'today']):
        self.select_date(period)
        self.fill_search_field(category)
        self.run_search()
