from datetime import date
from typing import List, Optional

from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship


class UserName(BaseModel):
    username: str


class User(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    username: str
    currency: str = "RUB"
    firstname: str
    surname: str
    currency: str
    photo: str | None = None
    photo_small: str | None = None
    full_name: str
    friendships_as_requester: List["Friendship"] = Relationship(
        back_populates="requester",
        sa_relationship_kwargs={"foreign_keys": "Friendship.requester_id"}
    )
    friendships_as_addressee: List["Friendship"] = Relationship(
        back_populates="addressee",
        sa_relationship_kwargs={"foreign_keys": "Friendship.addressee_id"}
    )


class Friendship(SQLModel, table=True):
    requester_id: str = Field(primary_key=True, foreign_key="user.id")
    addressee_id: str = Field(primary_key=True, foreign_key="user.id")
    status: str
    created_date: date
    requester: Optional[User] = Relationship(
        back_populates="friendships_as_requester",
        sa_relationship_kwargs={"foreign_keys": "[Friendship.requester_id]"}
    )
    addressee: Optional[User] = Relationship(
        back_populates="friendships_as_addressee",
        sa_relationship_kwargs={"foreign_keys": "[Friendship.addressee_id]"}
    )
