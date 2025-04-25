import logging
from datetime import datetime, timezone
from http import HTTPStatus
from typing import Literal
from urllib.parse import urljoin

import allure
import requests

from python_test.model.config import Envs
from python_test.model.db.category import Category
from python_test.model.db.spend import SpendAdd
from python_test.utils.sessions import BaseSession


class UserApiHelper:
    session: requests.Session
    base_url: str

    def __init__(self, envs: Envs):
        self.session = BaseSession(base_url=f'{envs.auth_url}')

    @allure.step('Создать пользователя {user_name}')
    def create_user(self, user_name: str, user_password: str):
        _resp = self.session.get('/register')
        data = {'username': user_name,
                'password': user_password,
                'passwordSubmit': user_password,
                '_csrf': _resp.cookies['XSRF-TOKEN']}
        response = self.session.post('', data)
        if response.status_code == HTTPStatus.CREATED:
            logging.info(f'Пользователь {user_name} зарегистрирован')
        else:
            logging.info(f'Пользователь {user_name} существует')


class SpendsHttpClient:
    session: requests.Session
    base_url: str
    base_url_spends: str
    base_url_categories: str

    def __init__(self, envs: Envs, token: str, user: str):
        self.session = BaseSession(base_url=envs.gateway_url)
        self.base_url_spends = urljoin(envs.gateway_url, "/api/spends")
        self.base_url_categories = urljoin(envs.gateway_url, "/api/categories")
        self.user_name = user
        self.session = requests.session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })

    @allure.step('Получить трату по id')
    def get_spend_by_id(self, spend_id: str):
        _resp = self.session.get(f'{self.base_url_spends}/{spend_id}')
        return SpendAdd.model_validate(_resp.json())

    @allure.step('Добавить новую трату')
    def add_spend(self, category: str,
                  amount: float,
                  currency: str = 'RUB',
                  desc: str = '',
                  date: datetime | str = None) -> SpendAdd:
        if currency not in ('RUB', 'KZT', 'EUR', 'USD'):
            raise ValueError('Не правильный тип валюты')
        if not date:
            date = datetime.now(timezone.utc)
        formatted_time = date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        category_spend = Category(name=category, username=self.user_name, archived=False)
        spend = SpendAdd(
            spendDate=formatted_time,
            category=category_spend,
            currency=currency,
            amount=amount,
            description=desc,
            username=self.user_name
        )
        _resp = self.session.post(f'{self.base_url_spends}/add', json=spend.model_dump())
        return SpendAdd.model_validate(_resp.json())

    @allure.step('Обновить трату')
    def update_spend(self, spend_id: str,
                     category: str,
                     amount: float,
                     currency: str = 'RUB',
                     desc: str = '',
                     date: datetime | str = None) -> SpendAdd:
        if currency not in ('RUB', 'KZT', 'EUR', 'USD'):
            raise ValueError('Не правильный тип валюты')
        if not date:
            date = datetime.now(timezone.utc)
        formatted_time = date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        category_spend = Category(name=category, username=self.user_name, archived=False)
        spend = SpendAdd(
            id=spend_id,
            spendDate=formatted_time,
            category=category_spend,
            currency=currency,
            amount=amount,
            description=desc,
            username=self.user_name
        )
        _resp = self.session.patch(f'{self.base_url_spends}/edit', json=spend.model_dump())
        return SpendAdd.model_validate(_resp.json())

    @allure.step('Получить id всех трат пользователя')
    def get_ids_all_spending(self) -> list[str]:
        ids = []
        for currency in ['RUB', 'KZT', 'USD', 'EUR']:
            _resp = self.session.get(f'{self.base_url_spends}/all?filterCurrency={currency}')
            body = _resp.json()
            ids += [spend['id'] for spend in body]
        return ids

    @allure.step('Получить id всех трат пользователя по типу валюты')
    def get_spending_ids_by_currency(self, currency: Literal['RUB', 'KZT', 'USD', 'EUR'] = 'RUB') -> list[str]:
        _resp = self.session.get(f'{self.base_url_spends}/all?filterCurrency={currency}')
        return [spend['id'] for spend in _resp.json()]

    @allure.step('Удалить трату')
    def delete_spending_by_id(self, spending_id: str) -> int:
        _resp = self.session.delete(f'{self.base_url_spends}/remove?ids={spending_id}')
        return _resp.status_code

    @allure.step('Удалить все траты пользователя')
    def delete_all_spending(self):
        spending_ids_lst = self.get_ids_all_spending()
        for spending_id in spending_ids_lst:
            self.delete_spending_by_id(spending_id)

    @allure.step('Добавить категорию')
    def add_category(self, category_name: str, archived: bool = False) -> Category:
        category_dict = {'name': category_name, 'username': self.user_name, 'archived': archived}
        _resp = self.session.post(f'{self.base_url_categories}/add', json=category_dict)
        return Category.model_validate(_resp.json())

    @allure.step('Обновить категорию')
    def update_category(self, category_id: str, category_name: str, archived: bool = False):
        category_dict = {"id": category_id, 'name': category_name, 'username': self.user_name, 'archived': archived}
        _resp = self.session.patch(f'{self.base_url_categories}/update', json=category_dict)
        return Category.model_validate(_resp.json())

    @allure.step('Получить id всех категорий пользователя')
    def get_ids_all_categories(self, exclude_archived: bool = False) -> list[str]:
        _resp = self.session.get(f'{self.base_url_categories}/all', params={'archived': exclude_archived})
        return [spend['id'] for spend in _resp.json()]
