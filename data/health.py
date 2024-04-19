import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Health(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'Health'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    weight = sqlalchemy.Column(sqlalchemy.Float)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("Users.id"))
    water = sqlalchemy.Column(sqlalchemy.Float)
    activity = sqlalchemy.Column(sqlalchemy.Integer)
    heart_rate = sqlalchemy.Column(sqlalchemy.Integer)
    mental = sqlalchemy.Column(sqlalchemy.Integer)
    steps = sqlalchemy.Column(sqlalchemy.Integer)
    user = orm.relationship('User')