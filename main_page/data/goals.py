import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm
import datetime
from .db_session import SqlAlchemyBase


class Goal(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'Goals'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    priority = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    finish_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                    default=datetime.datetime.now)
    user = orm.relationship('Users')