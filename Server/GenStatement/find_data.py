import logging
from flask import current_app
from geoalchemy2.functions import ST_Contains
from Server.GenStatement.orm import Request, Area,\
    Procuracy, AdminLevel, \
    ProblemFederalOffence, NarushFederalNPA, FedOffenceOrgType, \
    ProblemMunicipalOffence, NarushMunicNPA, MunicipalOffenceOrgType, \
    ProblemOffence, Offence, OsnVozbPravPoKoapRF, OsnovVozbOrgType, OsnVozbOffence, \
    OsnRassmSoobOPrav, OsnRasmOffence, \
    ProblemPetitionProblem, ProblemPetition, \
    OffencePetition, Petition, \
    ProblemOpinion, Opinion
from sqlalchemy.orm import Load
from sqlalchemy.sql.expression import or_
from sqlalchemy import desc

# from flask import render_template_string
from jinja2 import Template
from shapely import wkb
import datetime

from Server.api.orm import User


class Complaint():
    class AreaNotFound(Exception):
        def __init__(self, message, errors=None):
            super().__init__(message)
            self.errors = errors

    opinions = []
    bases_of_consideration = []
    offences_federal = []
    offences_municipal = []
    bases_of_excitation = []
    problem_petitions = []
    offence_petitions = []
    request = None
    problem = None
    area = None
    procuracy = None
    municipal_area = None
    site = None

    def __init__(self, request, problem):
        self.request = request
        request_id = request.id
        self.problem = problem
        db = current_app.config["database"]
        areas = Complaint.find_areas(db.session, request_id)
        data = Complaint.find_best_area(db.session, areas)
        if not data:
            raise Complaint.AreaNotFound("Bad coordinate region")
        self.area = data["area"]
        self.procuracy = data["procuracy"]
        self.municipal_area = data["municipal_area"]

    def continue_init(self):
        db = current_app.config["database"]
        org_type = self.procuracy.organisation_type_id
        problem_id = self.problem.id
        self.organisation_type = org_type
        self.offences_federal = Complaint.find_federal_offences(
            db.session,
            problem_id,
            org_type
        )
        if self.municipal_area:
            self.offences_municipal = Complaint.find_municipal_offences(
                db.session,
                problem_id,
                self.procuracy.organisation_type_id,
                self.municipal_area.id
            )
        resp = db.session.query(ProblemOffence, Offence). \
            join(Offence, ProblemOffence.offence_id == Offence.id). \
            filter(ProblemOffence.problem_id == problem_id)
        offences = list(map(lambda r: r[1], resp))
        self.offences = offences
        self.bases_of_excitation = Complaint.find_offence_koap(
            db.session,
            offences,
            org_type
        )
        self.bases_of_consideration = Complaint.find_basis_of_consideration(
            db.session,
            offences
        )
        self.problem_petitions = Complaint.find_problem_petitions(db.session, problem_id)
        self.offence_petitions = Complaint.find_offence_petitions(db.session, offences)
        self.opinions = Complaint.find_opinion(db.session, problem_id)
        return self

    def get_data(self):
        bases_of_excitation =  list(map(lambda o: o.text, self.bases_of_excitation))
        opinions = list(map(lambda o: o.text, self.opinions))
        bases_of_consideration = list(map(lambda o: o.text, self.bases_of_consideration))
        offences_federal = list(map(lambda o: o.text, self.offences_federal))
        offences_municipal = list(map(lambda o: o.text, self.offences_municipal))
        bases_of_excitation = list(map(lambda o: o.text, self.bases_of_excitation))
        problem_petitions = list(map(lambda o: o.text, self.problem_petitions))
        offence_petitions = list(map(lambda o: o.text, self.offence_petitions))
        offences = list(map(lambda o: o.text, self.offences))
        problem = self.problem.text
        point = wkb.loads(bytes(self.request.coordinate.data))
        coords = '(%f, %f)' % (point.x, point.y)
        # TODO: date still empty
        date = datetime.datetime.today().date().strftime("%d.%m.%Y")
        templ = Template(problem)
        problem = templ.render(coord=coords, date=date)
        db = current_app.config["database"]
        user = db.session.query(User).\
            filter(User.id == self.request.user_id).first()
        data = {
            "request_number": self.request.id,
            "organization_name": self.procuracy.name_prok,
            "site": self.procuracy.site,
            "user_name": user.name,
            "user_patronymic": user.patronymic,
            "user_surname": user.surname,
            "email": user.email,
            "photo": self.request.photo_path,
            "offences": offences,
            "problem": problem,
            "opinions": opinions,
            "bases_of_excitation": bases_of_excitation,
            "offences_federal": offences_federal,
            "offences_municipal": offences_municipal,
            "bases_of_consideration": bases_of_consideration,
            "offence_petitions": offence_petitions,
            "problem_petitions": problem_petitions,
            "order": [
                "offences",
                "problem",
                "opinion",
                "bases_of_excitation",
                "offences_federal",
                "offences_municipal",
                "bases_of_consideration",
                "offence_petitions",
                "problem_petitions"
            ]
        }
        return data

    @staticmethod
    def find_areas(session, request_id):
        resp = session.query(Area, Request). \
            filter(ST_Contains(Area.coordinate, Request.coordinate)). \
            filter(Request.id == request_id).\
            options(Load(Area).load_only("id"))
        # Returns 'Area' objects only.
        return list(map(lambda r: r[0], resp))

    @staticmethod
    def find_best_area(session, areas):
        # TODO: Депутаты тоже
        # TODO: написать в адин запрос (с FULL JOIN)
        resp = session.query(Area, Procuracy). \
            filter(or_(Area.id == a.id for a in areas)). \
            join(Procuracy, Area.id == Procuracy.area_id). \
            join(AdminLevel, Area.admin_level_id == AdminLevel.id). \
            order_by(desc(AdminLevel.number))
        # Нам нужно вернуть Area с миаксимальным административным уровнем
        # А так же, если это возможно, вернуть Area муниципального уровня
        try:
            area, procuracy = resp[0]
        except IndexError:
            logging.error("Cannot find area for this coordinate")
            return None

        resp = session.query(Area, AdminLevel). \
            filter(or_(Area.id == a.id for a in areas)). \
            join(AdminLevel, Area.admin_level_id == AdminLevel.id). \
            filter(AdminLevel.number == 6)
        municipal_area = None
        for a, lvl in resp:
            print("Area level:", lvl.number)
            municipal_area = a
        return {
            "area": area,
            "procuracy": procuracy,
            "municipal_area": municipal_area
        }


    @staticmethod
    def find_federal_offences(session, problem_id, org_type):
        resp = session.query(ProblemFederalOffence, NarushFederalNPA, FedOffenceOrgType).\
            join(NarushFederalNPA, ProblemFederalOffence.federal_offence_id == NarushFederalNPA.id). \
            join(FedOffenceOrgType, NarushFederalNPA.id == FedOffenceOrgType.federal_offence_id). \
            filter(ProblemFederalOffence.problem_id == problem_id).\
            filter(FedOffenceOrgType.organisationtype_id == org_type)
        return list(map(lambda r: r[1], resp))

    @staticmethod
    def find_municipal_offences(session, problem_id, org_type, area_id):
        resp = session.query(ProblemMunicipalOffence, NarushMunicNPA, MunicipalOffenceOrgType).\
            join(NarushMunicNPA, ProblemMunicipalOffence.municipal_offence_id == NarushMunicNPA.id).\
            join(MunicipalOffenceOrgType, NarushMunicNPA.id == MunicipalOffenceOrgType.municipal_offence_id). \
            filter(ProblemMunicipalOffence.problem_id == problem_id).\
            filter(MunicipalOffenceOrgType.organisationtype_id == org_type).\
            filter(NarushMunicNPA.area_id == area_id)
        return list(map(lambda r: r[1], resp))

    @staticmethod
    def find_offence_koap(session, offences, org_type):
        resp = session.query(OsnVozbPravPoKoapRF, OsnovVozbOrgType, OsnVozbOffence).\
            join(OsnovVozbOrgType, OsnovVozbOrgType.osnvozb_id == OsnVozbPravPoKoapRF.id).\
            join(OsnVozbOffence, OsnVozbPravPoKoapRF.id == OsnVozbOffence.osnvozb_id). \
            filter(or_(OsnVozbOffence.offence_id == o.id for o in offences)). \
            filter(OsnovVozbOrgType.organisationtype_id == org_type)
        return list(map(lambda r: r[0], resp))

    @staticmethod
    def find_basis_of_consideration(session, offences):
        resp = session.query(OsnRassmSoobOPrav, OsnRasmOffence). \
            join(OsnRasmOffence, OsnRasmOffence.osnrasm_id == OsnRassmSoobOPrav.id). \
            filter(or_(OsnRasmOffence.offence_id == o.id for o in offences))
        return list(map(lambda r: r[0], resp))

    @staticmethod
    def find_problem_petitions(session, problem_id):
        resp = session.query(ProblemPetitionProblem, ProblemPetition).\
            join(
                ProblemPetition,
                ProblemPetitionProblem.problem_petition_id == ProblemPetition.id
            ).\
            filter(ProblemPetitionProblem.problem_id == problem_id)
        return list(map(lambda r: r[1], resp))

    @staticmethod
    def find_offence_petitions(session, offences):
        resp = session.query(OffencePetition, Petition). \
            join(
            Petition,
            OffencePetition.petition_id == Petition.id
        ). \
            filter(or_(OffencePetition.offence_id == o.id for o in offences))
        return list(map(lambda r: r[1], resp))

    @staticmethod
    def find_opinion(session, problem_id):
        resp = session.query(ProblemOpinion, Opinion). \
            join(Opinion, ProblemOpinion.opinion_id == Opinion.id). \
            filter(ProblemOpinion.problem_id == problem_id)
        return list(map(lambda r: r[1], resp))
