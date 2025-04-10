import pytest


class TestData:
    category = lambda x: pytest.mark.parametrize("category", [x], indirect=True,
                                                 ids=lambda param: param['category_name'])
    spend = lambda x: pytest.mark.parametrize("spend", [x], indirect=True,
                                              ids=lambda param: f'{param['category']},{param['amount']}')
