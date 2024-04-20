import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import create_engine
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from datetime import date


class Ration(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'ration'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("Users.id"))
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    weight = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=date.today())
    total_kcal = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    total_proteins = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    total_fats = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    total_carbohydrates = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user = orm.relationship('User')
