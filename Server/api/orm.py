from sqlalchemy import Column, TIMESTAMP
from sqlalchemy import Integer, String
from sqlalchemy.ext.declarative import declarative_base

from geoalchemy2 import Geometry


Base = declarative_base()


class User(Base):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    surname = Column(String)
    patronymic = Column(String)
    email = Column(String)
    email_password = Column(String)


class Request(Base):
    __tablename__ = 'request'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    date = Column(TIMESTAMP)
    photo_path = Column(String)
    coordinate = Column(Geometry('POINT'))
    telegraph = Column(String)
    area_id = Column(Integer)
    problem_id = Column(Integer)
    request_status_id = Column(Integer)


class RequestStatus(Base):
    __tablename__ = 'requeststatus'
    id = Column(Integer, primary_key=True)
    text = Column(String)


class ProblemType(Base):
    __tablename__ = "problemtype"
    id = Column(Integer, nullable=True, autoincrement=True, primary_key=True)
    text = Column(String, nullable=True)


class Problem(Base):
    __tablename__ = "problem"
    id = Column(Integer, nullable=True, autoincrement=True, primary_key=True)
    name = Column(String, nullable=True)
    text = Column(String, nullable=True)
    problem_type_id = Column(Integer, nullable=True)
