from python_test.model.BasePage import BasePage
from python_test.model.LoginPage import LoginPageHelper
from python_test.model.MainPage import MainPageHelper
from python_test.model.SignUpPage import SignUpPageHelper
from python_test.model.SpendingPage import SpendingPageHelper


class Niffler(BasePage):

    def __init__(self, wd):
        super().__init__(wd)
        self.login_page = LoginPageHelper(self.wd)
        self.main_page = MainPageHelper(self.wd)
        self.sign_up_page = SignUpPageHelper(self.wd)
        self.spending_page = SpendingPageHelper(self.wd)
