import allure
import pytest
from faker import Faker

from python_test.data_helper.api_helper import UserApiHelper
from python_test.report_helper import Epic, Feature
from python_test.resources.templates.read_templates import (current_user_xml, update_user_xml, send_invitation_xml,
                                                            accept_invitation_xml, decline_invitation_xml, friends,
                                                            remove_friend)
from python_test.utils.sessions import SoapSession
from python_test.utils.xml_check import check_current_user_result_operation, get_friends_list

fake = Faker()


@pytest.fixture(scope='module')
def soap_session(envs):
    session = SoapSession(base_url=envs.soap_address)
    return session


@pytest.fixture()
def auth_helper(envs):
    auth_client = UserApiHelper(envs)
    result = auth_client.create_user(fake.name(), fake.password(special_chars=False))
    return result

@pytest.mark.parallel
@allure.epic(Epic.niffler)
@allure.feature(Feature.soap)
class TestSoapNiffler:

    @allure.title('Получение информации о существующем пользователе по его username')
    def test_get_user_info_by_exist_username(self, soap_session, envs):
        with allure.step(f'Выполнить запрос по пользователю {envs.test_username}'):
            response = soap_session.request(data=current_user_xml(envs.test_username))

        with allure.step('Проверить корректность ответа'):
            user_data = check_current_user_result_operation(response.text)
            assert user_data['username'] == envs.test_username
            with allure.step('Убедиться, что у пользователя есть id'):
                assert user_data['id'], 'У пользователя нет id'

    @allure.title('Запрос информации о незарегистрированном пользователе в системе по username')
    def test_get_user_info_by_not_exist_username(self, soap_session):
        user_name = fake.name()
        with allure.step(f'Выполнить запрос по пользователю {user_name}'):
            response = soap_session.request(data=current_user_xml(user_name))

        with allure.step('Проверить ответ'):
            user_data = check_current_user_result_operation(response.text)
            assert user_data['username'] == user_name
            with allure.step('Убедиться, что у пользователя в ответе отсутствует поле id'):
                assert not user_data['id'], 'У пользователя есть id'
            with allure.step('Убедиться, что у пользователя в ответе отсутствует поле fullname'):
                assert not user_data['fullname'], 'У пользователя есть поле fullname'

    @allure.title('Обновление полного имени и типа валюты у пользователя')
    def test_update_user(self, soap_session, envs, auth_helper, userdata_db):
        new_user = fake.name()
        with allure.step(f'Создать нового пользователя {new_user}'):
            UserApiHelper(envs).create_user(new_user, fake.password(special_chars=False))
            user_from_db = userdata_db.get_user(new_user)

        new_fullname = f'{fake.first_name()} {fake.last_name()}'
        new_currency = 'KZT'
        date_for_update = update_user_xml(str(user_from_db.id.__str__()), user_from_db.username, fullname=new_fullname,
                                          currency=new_currency)

        with allure.step(f'Выполнить запрос по обновлению пользователя {new_user}'):
            soap_session.request(data=date_for_update)
        with allure.step(f'Проверить измененные данные по пользователю {new_user} в БД'):
            update_user = userdata_db.get_user(new_user)
            assert update_user.full_name == new_fullname, 'Значение полного имени не обновилось'
            assert update_user.currency == new_currency, 'Значение типа валюты не обновилось'

    @allure.title('Отправка запроса на дружбу')
    def test_send_invitation(self, soap_session, envs, userdata_db):
        user_1, user_2 = fake.name(), fake.name()
        with allure.step(f'Создать пользователей {user_1} и {user_2} в системе'):
            UserApiHelper(envs).create_user(user_1, fake.password(special_chars=False))
            UserApiHelper(envs).create_user(user_2, fake.password(special_chars=False))
            user_1_from_db = userdata_db.get_user(user_1)
            user_2_from_db = userdata_db.get_user(user_2)

        with allure.step(f'Отправить запрос на дружбу от {user_1} к {user_2}'):
            soap_session.request(data=send_invitation_xml(user_1, user_2))

        with allure.step('Убедиться, что статус приглашения в БД == PENDING'):
            friendship = userdata_db.get_friendship(user_1_from_db.id.__str__(), user_2_from_db.id.__str__())
            assert friendship.status == 'PENDING', 'Статус != "PENDING"'

    @allure.title('Принятие запроса на дружбу')
    def test_accept_invitation(self, soap_session, envs, userdata_db):
        user_1, user_2 = fake.name(), fake.name()
        with allure.step(f'Создать пользователей {user_1} и {user_2} в системе'):
            UserApiHelper(envs).create_user(user_1, fake.password(special_chars=False))
            UserApiHelper(envs).create_user(user_2, fake.password(special_chars=False))
            user_1_from_db = userdata_db.get_user(user_1)
            user_2_from_db = userdata_db.get_user(user_2)

        with allure.step(f'Отправить запрос на дружбу от {user_1} к {user_2}'):
            soap_session.request(data=send_invitation_xml(user_1, user_2))

        with allure.step(f'Принять запрос на дружбу пользователем {user_2} от {user_1}'):
            soap_session.request(data=accept_invitation_xml(user_2, friend=user_1))

        with allure.step('Убедиться, что статус приглашения в БД == ACCEPTED'):
            friendship = userdata_db.get_friendship(user_1_from_db.id.__str__(), user_2_from_db.id.__str__())
            assert friendship.status == 'ACCEPTED', 'Статус != "ACCEPTED"'

    @allure.title('Отклонение запроса на дружбу')
    def test_decline_invitation(self, soap_session, envs, userdata_db):
        user_1, user_2 = fake.name(), fake.name()
        with allure.step(f'Создать пользователей {user_1} и {user_2} в системе'):
            UserApiHelper(envs).create_user(user_1, fake.password(special_chars=False))
            UserApiHelper(envs).create_user(user_2, fake.password(special_chars=False))
            user_1_from_db = userdata_db.get_user(user_1)
            user_2_from_db = userdata_db.get_user(user_2)

        with allure.step(f'Отправить запрос на дружбу от {user_1} к {user_2}'):
            soap_session.request(data=send_invitation_xml(user_1, user_2))

        with allure.step('Убедиться, что статус приглашения в БД == PENDING'):
            friendship = userdata_db.get_friendship(user_1_from_db.id.__str__(), user_2_from_db.id.__str__())
            assert friendship.status == 'PENDING', 'Статус != "PENDING"'

        with allure.step(f'Отклонить запрос на дружбу пользователем {user_2} от {user_1}'):
            soap_session.request(data=decline_invitation_xml(user_2, friend=user_1))

        with allure.step('Убедиться в отсутствии записи о дружбе в БД'):
            friendship = userdata_db.get_friendship(user_1_from_db.id.__str__(), user_2_from_db.id.__str__())
            assert not friendship, 'Есть запись о дружбе в БД'

    @allure.title('Получение списка друзей')
    def test_get_friends(self, soap_session, envs):
        user_1, user_2, user_3 = fake.name(), fake.name(), fake.name()
        with allure.step(f'Создать пользователей {user_1} и {user_2} в системе'):
            UserApiHelper(envs).create_user(user_1, fake.password(special_chars=False))
            UserApiHelper(envs).create_user(user_2, fake.password(special_chars=False))
            UserApiHelper(envs).create_user(user_3, fake.password(special_chars=False))

        with allure.step(f'Отправить запрос на дружбу от {user_1} к {user_2} и {user_3}'):
            soap_session.request(data=send_invitation_xml(user_1, user_2))
            soap_session.request(data=send_invitation_xml(user_1, user_3))

        with allure.step(f'Принять запрос на дружбу пользователями {user_2} и {user_3} от {user_1}'):
            soap_session.request(data=accept_invitation_xml(user_2, friend=user_1))
            soap_session.request(data=accept_invitation_xml(user_3, friend=user_1))

        with allure.step(f'Убедиться в наличии 2-ух друзей у пользователя {user_1}'):
            response = soap_session.request(data=friends(user_1))
            friends_list = get_friends_list(response.text)
            assert all(user['username'] in (user_2, user_3) for user in friends_list), 'Не все юзеры в списке друзей'
            assert all(user['friendshipStatus'] == 'FRIEND' for user in friends_list), 'Нет статуса Friend'

    @allure.title('Удаление друга')
    def test_remove_friend(self, soap_session, envs):
        user_1, user_2 = fake.name(), fake.name()
        with allure.step(f'Создать пользователей {user_1} и {user_2} в системе'):
            UserApiHelper(envs).create_user(user_1, fake.password(special_chars=False))
            UserApiHelper(envs).create_user(user_2, fake.password(special_chars=False))

        with allure.step(f'Отправить запрос на дружбу от {user_1} к {user_2}'):
            soap_session.request(data=send_invitation_xml(user_1, user_2))

        with allure.step(f'Принять запрос на дружбу пользователем {user_2} от {user_1}'):
            soap_session.request(data=accept_invitation_xml(user_2, friend=user_1))

        with allure.step(f'Убедиться в наличии друга у пользователя {user_1}'):
            response = soap_session.request(data=friends(user_1))
            friends_list = get_friends_list(response.text)
            assert len(friends_list) == 1
            friend = friends_list[0]
            assert friend['username'] == user_2
            assert friend['friendshipStatus'] == 'FRIEND'

        with allure.step('Удалить друга'):
            soap_session.request(data=remove_friend(username=user_1, friend=user_2))

        with allure.step(f'Убедиться, что список друзей пуст после удаления друга'):
            response = soap_session.request(data=friends(user_1))
            assert not get_friends_list(response.text)
