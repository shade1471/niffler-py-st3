from sqlmodel import SQLModel, Field


class Category(SQLModel, table=True):
    __mapper_args__ = {'confirm_deleted_rows': False}
    id: str = Field(default=None, primary_key=True)
    name: str
    username: str
    archived: bool
