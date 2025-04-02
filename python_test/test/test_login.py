import pytest
from selenium.webdriver.chrome.webdriver import WebDriver

from python_test.model.LoginPage import LoginPageHelper, LoginPage
from selenium import webdriver

from python_test.model.MainPage import MainPage


@pytest.fixture(scope="session")
def browser():
    wd = webdriver.Chrome()
    yield wd
    wd.quit()


def test_login(browser: WebDriver):
    niffler = LoginPageHelper(browser)
    niffler.go_to_niffler()
    assert 'Log in' == niffler.find_element(LoginPage.HEADER).text
    niffler.login_by_user('andrey', 'qwerty')
    assert niffler.find_element(MainPage.PROFILE_BUTTON).is_displayed()