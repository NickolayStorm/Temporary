from sqlalchemy import Column, TEXT, INTEGER, ForeignKey, DATE
# from sqlalchemy import Integer, String
from sqlalchemy.ext.declarative import declarative_base

from geoalchemy2 import Geometry
# from geoalchemy2.functions import ST_AsGeoJSON

Base = declarative_base()


class Problem(Base):
    __tablename__ = "problem"
    id = Column(INTEGER, nullable=True, autoincrement=True, primary_key=True)
    name = Column(TEXT, nullable=True)
    text = Column(TEXT, nullable=True)
    problem_type_id = Column(INTEGER, ForeignKey("problemtype.id"), nullable=True)


class Request(Base):
    __tablename__ = "request"
    id = Column(INTEGER, nullable=True, autoincrement=True, primary_key=True)
    user_id = Column(INTEGER, ForeignKey("User.id"), nullable=True)
    date = Column(DATE, nullable=True)
    coordinate = Column(TEXT, nullable=True)
    photo_path = Column(TEXT, nullable=True)
    telegraph = Column(INTEGER, nullable=True)
    request_status_id = Column(INTEGER, ForeignKey("RequestStatus.id"), nullable=True)
    problem_id = Column(INTEGER, ForeignKey("Problem.id"), nullable=True)
    Column('area_id', INTEGER, nullable=True)


class Area(Base):
    __tablename__ = "area"
    id = Column(INTEGER, nullable=True, autoincrement=True, primary_key=True)
    area_name = Column(TEXT, nullable=True)
    coordinate = Column(Geometry('MULTIPOLYGON'), nullable=True)
    boundary_id = Column(INTEGER, ForeignKey("Boundary.id"), nullable=True)
    region_id = Column(INTEGER, ForeignKey("Region.id"), nullable=True)
    admin_level_id = Column(INTEGER, ForeignKey("AdminLevel.id"), nullable=True)


class Procuracy(Base):
    __tablename__ = "procuracy"
    id = Column(INTEGER, nullable=True, autoincrement=True, primary_key=True)
    organisation_type_id = Column(INTEGER, ForeignKey("OrganisationType.id"), nullable=True)
    area_name = Column(TEXT, nullable=True)
    admin_level_id = Column(INTEGER, ForeignKey("AdminLevel.id"), nullable=True)
    area_id = Column(INTEGER, nullable=True)
    email_prok = Column(TEXT, nullable=True)
    type_prok = Column(TEXT, nullable=True)
    name_prok = Column(TEXT, nullable=True)
    site = Column(TEXT, nullable=True)


class AdminLevel(Base):
    __tablename__ = "adminlevel"
    id = Column(INTEGER, nullable=True, autoincrement=True, primary_key=True)
    number = Column(INTEGER, nullable=True)
    Column('text', TEXT, nullable=True)


class Offence(Base):
    __tablename__ = "offence"
    id = Column(INTEGER, nullable=True, autoincrement=True, primary_key=True)
    text = Column(TEXT, nullable=True)
    name = Column(TEXT, nullable=True)


class ProblemType(Base):
    __tablename__ = "problemtype"
    id = Column(INTEGER, nullable=True, autoincrement=True, primary_key=True)
    text = Column(TEXT, nullable=True)


class RequestStatus(Base):
    __tablename__ = "requeststatus"
    id = Column(INTEGER, nullable=True, autoincrement=True, primary_key=True)
    text = Column(TEXT, nullable=True)


class OrganizationType(Base):
    __tablename__ = "organisationtype"
    id = Column(INTEGER, nullable=True, autoincrement=True, primary_key=True)
    text = Column(TEXT, nullable=True)


class Boundary(Base):
    __tablename__ = "boundary"
    id = Column(INTEGER, nullable=True, autoincrement=True, primary_key=True)
    text = Column(TEXT, nullable=True)


class Region(Base):
    __tablename__ = "region"
    id = Column(INTEGER, nullable=True, autoincrement=True, primary_key=True)
    name = Column(TEXT, nullable=True)


class Opinion(Base):
    __tablename__ = "opinion"
    id = Column(INTEGER, nullable=True, autoincrement=True, primary_key=True)
    name = Column(TEXT, nullable=True)
    text = Column(TEXT, nullable=True)


class OsnVozbPravPoKoapRF(Base):
    __tablename__ = "osnvozb"
    id = Column(INTEGER, nullable=True, autoincrement=True, primary_key=True)
    name = Column(TEXT, nullable=True)
    text = Column(TEXT, nullable=True)


class NarushFederalNPA(Base):
    __tablename__ = "narushfederalnpa"
    id = Column(INTEGER, nullable=True, autoincrement=True, primary_key=True)
    name = Column(TEXT, nullable=True)
    text = Column(TEXT, nullable=True)


class NarushMunicNPA(Base):
    __tablename__ = "municipal_offence"
    id = Column(INTEGER, nullable=True, autoincrement=True, primary_key=True)
    name = Column(TEXT, nullable=True)
    text = Column(TEXT, nullable=True)
    area_id = Column(INTEGER, ForeignKey("area.id"))


class OsnRassmSoobOPrav(Base):
    __tablename__ = "osnrasm"
    id = Column(INTEGER, nullable=True, autoincrement=True, primary_key=True)
    name = Column(TEXT, nullable=True)
    text = Column(TEXT, nullable=True)


class Petition(Base):
    __tablename__ = "petition"
    id = Column(INTEGER, nullable=True, autoincrement=True, primary_key=True)
    name = Column(TEXT, nullable=True)
    text = Column(TEXT, nullable=True)


class Document(Base):
    __tablename__ = "document"
    id = Column(INTEGER, nullable=True, autoincrement=True, primary_key=True)
    request_id = Column(INTEGER, ForeignKey("Request.id"), nullable=True)
    offence_id = Column(INTEGER, nullable=True)
    opinion_id = Column(INTEGER, nullable=True)


class Deputy(Base): 
    __tablename__ = "deputy"
    id = Column(INTEGER, nullable=True, autoincrement=True, primary_key=True)
    organisation_id = Column(INTEGER, ForeignKey("organisationtype.id"), nullable=True)
    admin_level_id = Column(INTEGER, ForeignKey("adminlevel.id"), nullable=True)


class ProblemOffence(Base):
    __tablename__ = "problem_offence"
    problem_id = Column(INTEGER, ForeignKey("problem.id"), nullable=True, autoincrement=True, primary_key=True)
    offence_id = Column(INTEGER, ForeignKey("offence.id"), nullable=True)


class ProblemOpinion(Base):
    __tablename__ = "problem_opinion"
    problem_id = Column(INTEGER, ForeignKey("problem.id"), nullable=True, autoincrement=True, primary_key=True)
    opinion_id = Column(INTEGER, ForeignKey("opinion.id"), nullable=True)


class ProblemFederalOffence(Base):
    __tablename__ = "problem_federal_offence"
    problem_id = Column(INTEGER, ForeignKey("problem.id"), nullable=True, autoincrement=True, primary_key=True)
    federal_offence_id = Column(INTEGER, ForeignKey("narushfederalnpa.id"), nullable=True)


class ProblemMunicipalOffence(Base):
    __tablename__ = "problem_municipal_offence"
    problem_id = Column(INTEGER, nullable=True, autoincrement=True, primary_key=True)
    municipal_offence_id = Column(INTEGER, ForeignKey("narushmunicnpa.id"), ForeignKey("problem.id"), nullable=True)


class ProblemPetition(Base):
    __tablename__ = "problem_petition"
    id = Column(INTEGER, nullable=True, autoincrement=True, primary_key=True)
    name = Column(TEXT, nullable=True)
    text = Column(TEXT, nullable=True)


class ProblemPetitionProblem(Base):
    __tablename__ = "problem_petition_problem"
    problem_id = Column(INTEGER, ForeignKey("problem.id"), nullable=True, autoincrement=True, primary_key=True)
    problem_petition_id = Column(INTEGER, ForeignKey("problem_petition.id"), nullable=True)


class OffencePetition(Base):
    __tablename__ = "offence_petition"
    offence_id = Column(INTEGER, ForeignKey("offence.id"), nullable=True, autoincrement=True, primary_key=True)
    petition_id = Column(INTEGER, ForeignKey("petition.id"), nullable=True)


class FedOffenceOrgType(Base):
    __tablename__ = "fed_offence_org_type"
    federal_offence_id = Column(INTEGER, ForeignKey("narushfederalnpa.id"), primary_key=True)
    organisationtype_id = Column(INTEGER, ForeignKey("organisationtype.id"), primary_key=True)


class MunicipalOffenceOrgType(Base):
    __tablename__ = 'mun_offence_org_type'
    municipal_offence_id = Column(INTEGER, ForeignKey("narushmunicnpa.id"), primary_key=True)
    organisationtype_id = Column(INTEGER, ForeignKey("organisationtype.id"), primary_key=True)


class OsnovVozbOrgType(Base):
    __tablename__ = 'osnvozb_org_type'
    osnvozb_id = Column(INTEGER, ForeignKey("osnvozbpravpokoaprf.id"), primary_key=True)
    organisationtype_id = Column(INTEGER, ForeignKey("organisationtype.id"), primary_key=True)


class OsnVozbOffence(Base):
    __tablename__ = 'osnvozb_offence'
    osnvozb_id = Column(INTEGER, ForeignKey("osnvozb.id"), primary_key=True)
    offence_id = Column(INTEGER, ForeignKey("offence.id"), primary_key=True)


class OsnRasmOffence(Base):
    __tablename__ = 'osnrasm_offence'
    osnrasm_id = Column(INTEGER, ForeignKey("osnrasm.id"), primary_key=True)
    offence_id = Column(INTEGER, ForeignKey("offence.id"), primary_key=True)


# INSERT INTO request(coordinate, problem_id) VALUES(ST_PointFromText('POINT(55.964107 54.719195)', 4326), 1);

# WITH cds AS(SELECT area.area_name, area.id, ST_Contains(area.coordinate, request.coordinate) AS contained FROM request, area)SELECT * from cds WHERE cds.contained=TRUE;