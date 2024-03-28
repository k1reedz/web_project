from datetime import date

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine("sqlite:///db/ration.db")
Base = declarative_base()


class Ration(Base):
    __tablename__ = 'ration'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    weight = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=date.today())
    total_kcal = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    total_proteins = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    total_fats = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    total_carbohydrates = sqlalchemy.Column(sqlalchemy.String, nullable=True)


Base.metadata.create_all(engine)