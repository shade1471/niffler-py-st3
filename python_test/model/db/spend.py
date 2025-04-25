from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from sqlmodel import SQLModel, Field

from python_test.model.db.category import Category


class Spend(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    username: str
    spend_date: datetime
    currency: str
    amount: float
    description: str
    category_id: str = Field(foreign_key="category.id")


class SpendAdd(BaseModel):
    id: Optional[str] = None
    spendDate: str
    category: Category
    currency: str = 'RUB'
    amount: float
    description: str = ''
    username: str
