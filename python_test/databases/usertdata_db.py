import time

import allure
from allure_commons.types import AttachmentType
from sqlalchemy import create_engine, Engine, event
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select

from python_test.model.config import Envs
from python_test.model.db.user import User, Friendship


def wait_for_record(session, model, max_retries=5, initial_delay=0.1, **filters):
    delay = initial_delay
    for attempt in range(max_retries):
        try:
            record = session.exec(select(model).filter_by(**filters)).one()
            return record
        except NoResultFound:
            if attempt == max_retries - 1:
                raise
            time.sleep(delay)
            delay *= 2


class UserdataDb:
    engine: Engine

    def __init__(self, envs: Envs):
        self.engine = create_engine(envs.userdata_db_url)
        event.listen(self.engine, "do_execute", fn=self.attach_sql)

    @staticmethod
    def attach_sql(cursor, statement, parameters, context):
        statement_with_params = statement % parameters
        command_name = statement.split(" ")[0]
        if command_name.isupper():
            name = f'{command_name} {context.engine.url.database}'
            allure.attach(statement_with_params, name=name, attachment_type=AttachmentType.TEXT)

    def get_user(self, username: str) -> User:
        with Session(self.engine) as session:
            wait_for_record(session, User, username=username)
            statement = select(User).where(User.username == username)
            return session.exec(statement).one()

    def get_friendship(self, user_uuid: str, user_to_uuid: str):
        with Session(self.engine) as session:
            statement = select(Friendship).where(Friendship.requester_id == user_uuid,
                                                 Friendship.addressee_id == user_to_uuid)
            try:
                return session.exec(statement).one()
            except NoResultFound:
                return None
