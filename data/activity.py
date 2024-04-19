import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine("sqlite:///db/activity.db")
Base = declarative_base()


class Activity(Base):
    __tablename__ = 'Activity'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    type = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    start = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    end = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)


Base.metadata.create_all(engine)
