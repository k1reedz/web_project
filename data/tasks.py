import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm
from datetime import time
from .db_session import SqlAlchemyBase


class Task(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'Tasks'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    task_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("Users.id"))
    weekday = sqlalchemy.Column(sqlalchemy.String)
    start = sqlalchemy.Column(sqlalchemy.Time, default=time(hour=0, minute=0, second=0))
    end = sqlalchemy.Column(sqlalchemy.Time, default=time(hour=0, minute=0, second=0))
    user = orm.relationship('User')