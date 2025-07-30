import allure
import grpc
import pytest
from google.protobuf import empty_pb2

from python_test.internal.pb.niffler_currency_pb2 import CalculateRequest, CurrencyValues
from python_test.internal.pb.niffler_currency_pb2_pbreflect import NifflerCurrencyServiceClient
from python_test.report_helper import Feature, Epic

@pytest.mark.parallel
@allure.epic(Epic.niffler)
@allure.feature(Feature.grpc)
class TestGrpcCurrencies:
    _curr = {1: 'RUB', 2: 'USD', 3: 'EUR', 4: 'KZT'}

    @allure.title('Конвертация валют')
    @pytest.mark.parametrize('spend, spend_currency, desired_currency, expected_result', [
        (100.0, CurrencyValues.EUR, CurrencyValues.RUB, 7200),
        (100.0, CurrencyValues.RUB, CurrencyValues.EUR, 1.39),
        (100.0, CurrencyValues.USD, CurrencyValues.RUB, 6666.67),
        (100.0, CurrencyValues.RUB, CurrencyValues.USD, 1.5),
        (100.0, CurrencyValues.USD, CurrencyValues.USD, 100.0),
        (100.0, CurrencyValues.KZT, CurrencyValues.USD, 0.21),
        (100.0, CurrencyValues.USD, CurrencyValues.KZT, 47619.05),
    ])
    def test_currency_conversion(self, grpc_client: NifflerCurrencyServiceClient,
                                 spend: float,
                                 spend_currency: CurrencyValues,
                                 desired_currency: CurrencyValues,
                                 expected_result: float
                                 ):
        with allure.step(f'Перевести 100 {self._curr[spend_currency]} в {self._curr[desired_currency]}'):
            response = grpc_client.calculate_rate(
                request=CalculateRequest(
                    spendCurrency=spend_currency,
                    desiredCurrency=desired_currency,
                    amount=spend
                ))
        with allure.step(f'Проверить, что ожидаемое значение равно {expected_result}'):
            assert response.calculatedAmount == expected_result, f'Expected {expected_result}'

    @allure.title('Отправка запроса на конвертацию без значения типа требуемой валюты')
    def test_calculate_rate_without_desired_currency(self, grpc_client: NifflerCurrencyServiceClient):
        with allure.step('Отправить запрос на конвертацию без обязательного значения требуемой валюты'):
            try:
                grpc_client.calculate_rate(
                    request=CalculateRequest(
                        spendCurrency=CurrencyValues.EUR,
                        amount=100.0
                    )
                )
            except grpc.RpcError as e:
                with allure.step('Проверить сообщение об ошибке'):
                    assert e.code() == grpc.StatusCode.UNKNOWN
                    assert e.details() == "Application error processing RPC"

    @allure.title('Отправка запроса на конвертацию без значения типа конвертируемой валюты')
    def test_calculate_rate_without_spend_currency(self, grpc_client: NifflerCurrencyServiceClient):
        with allure.step('Отправить запрос на конвертацию без обязательного значения конвертируемой валюты'):
            try:
                grpc_client.calculate_rate(
                    request=CalculateRequest(
                        desiredCurrency=CurrencyValues.RUB,
                        amount=100.0
                    )
                )
            except grpc.RpcError as e:
                with allure.step('Проверить сообщение об ошибке'):
                    assert e.code() == grpc.StatusCode.UNKNOWN
                    assert e.details() == "Application error processing RPC"

    @allure.title('Отправка запроса на конвертацию без значения суммы')
    def test_calculate_rate_without_amount(self, grpc_client: NifflerCurrencyServiceClient):
        with allure.step('Отправить запрос на конвертацию без обязательного поля суммы'):
            try:
                grpc_client.calculate_rate(
                    request=CalculateRequest(
                        spendCurrency=CurrencyValues.EUR,
                        desiredCurrency=CurrencyValues.RUB,
                    )
                )
            except grpc.RpcError as e:
                with allure.step('Проверить сообщение об ошибке'):
                    assert e.code() == grpc.StatusCode.UNKNOWN
                    assert e.details() == "Application error processing RPC"

    @allure.title('Получение всех поддерживаемых типов валют')
    def test_get_all_currencies(self, grpc_client: NifflerCurrencyServiceClient):
        with allure.step('Запросить все типы валют'):
            response = grpc_client.get_all_currencies(empty_pb2.Empty())
        with allure.step('Убедиться, что общее количество типов валют равно 4'):
            assert len(response.allCurrencies) == 4
