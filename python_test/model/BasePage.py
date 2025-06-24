import os

from dotenv import load_dotenv
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

load_dotenv()


class BasePage:

    def __init__(self, driver):
        self.wd = driver
        self.base_url = os.getenv('FRONTEND_URL')
        self.sign_up_url = f'{os.getenv('AUTH_URL')}/register'

    def find_element(self, locator: tuple[str, str], timeout=15) -> WebElement:
        return WebDriverWait(self.wd, timeout).until(EC.presence_of_element_located(locator),
                                                     message=f"Can't find element by locator {locator}")

    def find_elements(self, locator: tuple[str, str], timeout=15) -> list[WebElement]:
        return WebDriverWait(self.wd, timeout).until(EC.presence_of_all_elements_located(locator),
                                                     message=f"Can't find elements by locator {locator}")

    def get_element_property(self, locator: tuple[str, str], property_name: str, timeout: int = 10) -> str | int:
        element = WebDriverWait(self.wd, timeout).until(EC.presence_of_element_located(locator))
        WebDriverWait(self.wd, timeout).until(EC.visibility_of(element))
        return self.wd.execute_script(f"return arguments[0].{property_name};", element)

    def is_element_have_property(self, locator: tuple[str, str], property_name: str, values: list) -> bool:
        return self.get_element_property(locator, property_name) in values

    def wait_element_staleness_of(self, locator: tuple[str, str], timeout=10):
        element = self.find_element(locator)
        WebDriverWait(self.wd, timeout).until(EC.staleness_of(element))

    def wait_while_len_elements_not_equal(self, locator: tuple[str, str], value: int, timeout=10):
        """Ожидание пока длина списка элементов не станет отличаться от заданного значения"""
        WebDriverWait(self.wd, timeout).until(lambda d: len(d.find_elements(*locator)) != value)

    def wait_element_to_be_clickable(self, locator: tuple[str, str], timeout=10):
        return WebDriverWait(self.wd, timeout).until(EC.element_to_be_clickable(locator))

    def wait_element_becomes_visible(self, locator: tuple[str, str], timeout=10):
        element = self.find_element(locator)
        return WebDriverWait(self.wd, timeout).until(EC.visibility_of(element),
                                                     message=f"Element not visibility by locator {locator}")
