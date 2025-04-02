from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BasePage:

    def __init__(self, driver):
        self.wd = driver
        self.base_url = "http://frontend.niffler.dc/"

    def go_to_niffler(self):
        return self.wd.get(self.base_url)

    def find_element(self, locator, time=10):
        return WebDriverWait(self.wd, time).until(EC.presence_of_element_located(locator),
                                                  message=f"Can't find element by locator {locator}")

    def find_elements(self, locator, time=10):
        return WebDriverWait(self.wd, time).until(EC.presence_of_all_elements_located(locator),
                                                  message=f"Can't find elements by locator {locator}")

    def wait_visibility_of_element(self, *locator, timeout=10):
        """
        Ожидание видимости элемента
        :param locator: кортеж (By.CSS_SELECTOR, 'selector_here')
        :param timeout: Задаваемый timeout ожидания
        """
        el = self.wd.find_element(*locator)
        WebDriverWait(self.wd, timeout).until(EC.visibility_of(el))
