from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from model.BasePage import BasePage


class ProfilePage:
    CATEGORY_FIELD = (By.ID, 'category')
    CATEGORY_FIELD_ERROR = (By.CSS_SELECTOR, 'svg[data-testid="ErrorOutlineOutlinedIcon"]')
    CHECKBOX_ARCHIVED = (By.CSS_SELECTOR, 'input.PrivateSwitchBase-input')
    ALERT_MESSAGE = (By.CSS_SELECTOR, '.MuiAlert-message div')


class ProfilePageHelper(BasePage):

    def add_category(self, category: str):
        self.find_element(ProfilePage.CATEGORY_FIELD).clear()
        self.find_element(ProfilePage.CATEGORY_FIELD).send_keys(category)
        self.find_element(ProfilePage.CATEGORY_FIELD).send_keys(Keys.RETURN)

    def show_archived(self):
        self.find_element(ProfilePage.CHECKBOX_ARCHIVED).click()
