from sqlalchemy import Column, TIMESTAMP
from sqlalchemy import Integer, String
from sqlalchemy.ext.declarative import declarative_base

from geoalchemy2 import Geometry
# from geoalchemy2.functions import ST_AsGeoJSON

Base = declarative_base()


class Quarter(Base):
    __tablename__ = 'quarter'
    id = Column(Integer, primary_key=True)
    coords = Column(Geometry('MULTIPOLYGON'))


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    surname = Column(String)
    patronymic = Column(String)
    email = Column(String)
    password = Column(String)


class Request(Base):
    __tablename__ = 'request'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    date = Column(TIMESTAMP)
    coordinate = Column(Geometry('POINT'))
    telegraph = Column(String)
    area_id = Column(Integer)
    status_id = Column(Integer)
    category_id = Column(Integer)
    area = Column(Integer)


class Status(Base):
    __tablename__ = 'status'
    id = Column(Integer, primary_key=True)
    typename = Column(String)
    hierarchy = Column(Integer)


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    text = Column(String)
    category_id = Column(Integer)


class Area(Base):
    __tablename__ = 'area'
    id = Column(Integer, primary_key=True)
    area_name = Column(String)
    coordinates = Column(Geometry('MULTIPOLYGON'))
    area_type_directory_id = Column(Integer)
    organisation_id = Column(Integer)


class Organisation(Base):
    __tablename__ = 'organisation'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    url = Column(String)
    email = Column(String)


class AreaTypeDirectory(Base):
    __tablename__ = 'area_type_directory'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    hierarchy = Column(Integer)


class Template(Base):
    __tablename__ = 'template'
    id = Column(Integer, primary_key=True)
    text = Column(String)
    area_id = Column(Integer)
    id2 = Column(Integer)
