from python_test.model.LoginPage import LoginPage
from python_test.model.MainPage import MainPage
from python_test.model.ProfilePage import ProfilePage
from python_test.model.SignUpPage import SignUpPage
from python_test.model.SpendingPage import SpendingPage


class Niffler:

    def __init__(self, wd):
        self.login_page = LoginPage(wd)
        self.main_page = MainPage(wd)
        self.sign_up_page = SignUpPage(wd)
        self.spending_page = SpendingPage(wd)
        self.profile_page = ProfilePage(wd)
