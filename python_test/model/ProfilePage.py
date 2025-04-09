from urllib.parse import urljoin

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from model.BasePage import BasePage


class ProfilePage(BasePage):
    CATEGORY_FIELD = (By.ID, 'category')
    CATEGORY_FIELD_ERROR = (By.CSS_SELECTOR, 'svg[data-testid="ErrorOutlineOutlinedIcon"]')
    CHECKBOX_ARCHIVED = (By.CSS_SELECTOR, 'input.PrivateSwitchBase-input')
    ALERT_MESSAGE = (By.CSS_SELECTOR, '.MuiAlert-message div')
    ARCHIVE_BUTTON = (By.CSS_SELECTOR, 'button[aria-label="Archive category"]')
    CONFIRM_ARCHIVE_BUTTON = (By.CSS_SELECTOR, '[role="dialog"] .MuiButton-contained')
    CONFIRM_ARCHIVE_ALERT = (By.CSS_SELECTOR, '.MuiAlert-message div')
    ERROR_ELEMENT = (By.CSS_SELECTOR, '[data-testid="ErrorOutlineIcon"]')

    def is_page_load(self):
        return self.wait_element_becomes_visible(self.CATEGORY_FIELD).is_displayed()

    def open_profile_page(self):
        self.wd.get(urljoin(self.base_url, '/profile'))
        assert self.is_page_load(), 'Страница профиля не открылась'

    def add_category(self, category: str):
        self.find_element(self.CATEGORY_FIELD).clear()
        self.find_element(self.CATEGORY_FIELD).send_keys(category)
        self.find_element(self.CATEGORY_FIELD).send_keys(Keys.RETURN)

    def show_archived(self):
        self.find_element(self.CHECKBOX_ARCHIVED).click()

    def is_categories_field_disabled(self):
        category_field = self.find_element(self.CATEGORY_FIELD)
        return bool(category_field.get_attribute('disabled'))

    def get_text_error_category_field(self):
        return self.find_element(self.CATEGORY_FIELD_ERROR).get_attribute('aria-label')

    def get_text_alert_message(self):
        return self.find_element(ProfilePage.ALERT_MESSAGE).text

    def wait_error_alert_become_visible(self):
        self.wait_element_becomes_visible(self.ERROR_ELEMENT)

    def set_archive_category(self):
        self.find_element(self.ARCHIVE_BUTTON).click()
        self.wait_element_to_be_clickable(self.CONFIRM_ARCHIVE_BUTTON).click()
        self.wait_element_becomes_visible(self.CONFIRM_ARCHIVE_ALERT)
