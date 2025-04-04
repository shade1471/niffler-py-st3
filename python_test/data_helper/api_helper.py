import logging
from datetime import datetime, timezone
from http import HTTPStatus
from typing import Literal

import requests

LOG_IN_URL = 'http://auth.niffler.dc:9000/login'
SIGN_UP_URL = 'http://auth.niffler.dc:9000/register'
GATEWAY_URL = 'http://gateway.niffler.dc:8090'


def create_user(user_name: str, user_password: str):
    with requests.Session() as session:
        _resp = session.get(SIGN_UP_URL)
        data = {'username': user_name,
                'password': user_password,
                'passwordSubmit': user_password,
                '_csrf': _resp.cookies['XSRF-TOKEN']}
        response = session.post(SIGN_UP_URL, data)
    if response.status_code == HTTPStatus.CREATED:
        logging.info(f'Пользователь {user_name} зарегистрирован')
    else:
        logging.info(f'Пользователь {user_name} существует')


class UserApiHelper:

    def __init__(self, token: str):
        self.base_url_spends = f'{GATEWAY_URL}/api/spends'
        self.base_url_categories = f'{GATEWAY_URL}/api/categories'
        self.session = requests.session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })

    def add_spend(self, user_name: str, category: str, amount: int, currency='RUB', desc: str = '',
                  date: datetime = None) -> int:
        if currency not in ('RUB', 'KZT', 'EUR', 'USD'):
            raise ValueError('Не правильный тип валюты')
        if not date:
            date = datetime.now(timezone.utc)
        formatted_time = date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        spend_dict = {
            "spendDate": formatted_time,
            "category": {
                "name": category,
                "username": user_name,
                "archived": True
            },
            "currency": currency,
            "amount": amount,
            "description": desc,
            "username": user_name
        }

        _resp = self.session.post(f'{self.base_url_spends}/add', json=spend_dict)
        return _resp.status_code

    def get_ids_all_spending(self, currency: Literal['RUB', 'KZT', 'USD', 'EUR'] = 'RUB'):
        _resp = self.session.get(f'{self.base_url_spends}/all?filterCurrency={currency}')
        assert _resp.status_code == HTTPStatus.OK
        body = _resp.json()
        return [spend['id'] for spend in body]

    def remove_all_spending(self):
        spending_ids_lst = self.get_ids_all_spending()
        for spending_id in spending_ids_lst:
            _resp = self.session.delete(f'{self.base_url_spends}/remove?ids={spending_id}')
            assert _resp.status_code == HTTPStatus.OK

    def add_category(self, user_name: str, category_name: str) -> int:
        category_dict = {'name': category_name, 'username': user_name}
        _resp = self.session.post(f'{self.base_url_categories}/add', json=category_dict)
        return _resp.status_code
