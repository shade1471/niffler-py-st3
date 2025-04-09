import pytest

class Pages:
    profile_page = pytest.mark.usefixtures("profile_page")

class TestData:
    category = lambda x: pytest.mark.parametrize("category", [x], indirect=True)
    # category = lambda x: pytest.mark.parametrize("category", [x], indirect=True, ids=lambda param: param.description)