from datetime import datetime
from typing import Literal

from selenium.webdriver.common.by import By

from python_test.model.BasePage import BasePage


class SpendingPage(BasePage):
    AMOUNT_FIELD = (By.ID, 'amount')
    AMOUNT_HELPER_TEXT = (By.CSS_SELECTOR, '[id="amount"] + .input__helper-text')
    CURRENCY_FIELD = (By.ID, 'currency')
    CURRENCY_FIELD_TEXT = (By.CSS_SELECTOR, '[id = "currency"] span + span')
    CURRENCY_RUB_VALUE = (By.CSS_SELECTOR, 'li[data-value="RUB"]')
    CURRENCY_USD_VALUE = (By.CSS_SELECTOR, 'li[data-value="USD"]')
    CURRENCY_EUR_VALUE = (By.CSS_SELECTOR, 'li[data-value="EUR"]')
    CURRENCY_KZT_VALUE = (By.CSS_SELECTOR, 'li[data-value="KZT"]')
    CATEGORY_FIELD = (By.ID, 'category')
    CATEGORY_HELPER_TEXT = (By.CSS_SELECTOR, '[id="category"] + .input__helper-text')
    DESCRIPTION_FIELD = (By.ID, 'description')
    DATE_FIELD = (By.NAME, 'date')
    ALERT = (By.CSS_SELECTOR, '.MuiAlert-message')
    ADD_BUTTON = (By.ID, 'save')

    def fill_amount(self, value: int):
        el = self.find_element(self.AMOUNT_FIELD)
        el.clear()
        el.send_keys(str(value))

    def fill_category(self, category: str):
        el = self.find_element(self.CATEGORY_FIELD)
        el.clear()
        el.send_keys(category)

    def fill_date(self, date: datetime):
        formatted_time = date.strftime('%m%d%Y')
        el = self.find_element(self.DATE_FIELD)
        el.click()
        el.send_keys(formatted_time)

    def fill_description(self, desc: str):
        el = self.find_element(self.DESCRIPTION_FIELD)
        el.clear()
        el.send_keys(desc)

    def select_currency(self, currency: Literal['RUB', 'KZT', 'USD', 'EUR']):
        currency_locator = {'RUB': self.CURRENCY_RUB_VALUE, 'USD': self.CURRENCY_USD_VALUE,
                            'KZT': self.CURRENCY_KZT_VALUE, 'EUR': self.CURRENCY_EUR_VALUE}
        self.find_element(self.CURRENCY_FIELD).click()
        self.find_element(currency_locator[currency]).click()
        assert self.find_element(self.CURRENCY_FIELD_TEXT).text == currency

    def click_save(self):
        self.find_element(self.ADD_BUTTON).click()

    def add_new_spending(self, amount: int, category: str, date: datetime = None, desc: str = None):
        self.fill_amount(amount)
        self.fill_category(category)
        if date:
            self.fill_date(date)
        if desc:
            self.fill_description(desc)
        self.click_save()

    def get_amount_field_helper_text(self) -> str:
        return self.find_element(self.AMOUNT_HELPER_TEXT).text

    def get_category_field_helper_text(self) -> str:
        return self.find_element(self.CATEGORY_HELPER_TEXT).text
