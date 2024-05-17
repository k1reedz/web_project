import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Activity(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'Activity'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    type = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    start = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    end = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("Users.id"))
    user = orm.relationship('User')