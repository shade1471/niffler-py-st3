import json
import logging

import allure
import pytest
from faker import Faker

from python_test.data_helper.api_helper import UserApiHelper
from python_test.data_helper.kafka_client import KafkaClient
from python_test.databases.usertdata_db import UserdataDb
from python_test.model.config import Envs
from python_test.model.db.user import UserName
from python_test.report_helper import Epic, Feature


@pytest.mark.sequential
@allure.epic(Epic.niffler)
@allure.feature(Feature.kafka)
class TestKafka:

    @allure.title('Убедиться в наличии сообщения в Kafka после успешной регистрации нового пользователя')
    def test_message_should_be_produced_to_kafka_after_successful_registration(self, kafka: KafkaClient, envs: Envs):
        username = Faker().user_name()
        password = Faker().password(special_chars=False)

        topic_partitions = kafka.subscribe_listen_new_offsets('users')

        with allure.step('Зарегистрировать нового пользователя'):
            auth_client = UserApiHelper(envs)
            result = auth_client.create_user(username, password)
            assert result.status_code == 201

        event = kafka.log_msg_and_json(topic_partitions)

        with allure.step("Проверить, что сообщение из Kafka существует"):
            assert event != '' and event != b''

        with allure.step("Проверить содержимое сообщения"):
            event_decode = json.loads(event.decode('utf8'))
            UserName.model_validate(event_decode)
            assert event_decode['username'] == username

    @allure.title('Сервис niffler-userdata должен забирать сообщение из топика Kafka')
    def test_niffler_userdata_should_consume_message_from_kafka(self, kafka: KafkaClient, userdata_db: UserdataDb):
        with allure.step('Отправить сообщение в Kafka'):
            user_name_for_msg = Faker().user_name()
            logging.info(f'Отправить сообщение по пользователю: {user_name_for_msg}')
            kafka.send_message("users", user_name_for_msg)
        with allure.step('Убедиться, что в таблице userdata есть запись о пользователе из сообщения'):
            user_from_db = userdata_db.get_user(username=user_name_for_msg)
            assert user_from_db.username == user_name_for_msg
