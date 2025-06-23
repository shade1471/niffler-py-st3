from sqlalchemy import create_engine, Engine, event
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select

import allure
from allure_commons.types import AttachmentType

from collections.abc import Sequence

from python_test.model.config import Envs
from python_test.model.db.user import User, Friendship


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
