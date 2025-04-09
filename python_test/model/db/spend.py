from datetime import datetime

from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship


class Category(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    name: str
    username: str
    archived: bool


class Spend(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    username: str
    spendDate: datetime
    currency: str
    amount: float
    description: str
    category_id: str = Field(foreign_key="category.id")


class SpendAdd(BaseModel):
    amount: float
    description: str
    category: str
    spendDate: str
    currency: str
