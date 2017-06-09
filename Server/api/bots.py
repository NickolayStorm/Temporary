import logging
from datetime import datetime
from flask import current_app, Blueprint, request
from .view import ok, error
from .orm import User, Request, \
    RequestStatus, ProblemType, Problem
from sqlalchemy.orm import Load
from geoalchemy2.elements import WKTElement

from Server import GenStatement
from Server.GenStatement import Complaint
import Server.Post as Post
from Server.AppealScripts import create_appeal


bots = Blueprint('bot', __name__)


@bots.route('/create/user', methods=['POST'])
def create_user():
    logging.info("/create/user")
    db = current_app.config["database"]
    user = User()
    db.session.add(user)
    db.session.commit()
    db.session.refresh(user)
    logging.info("Created user id(%s)" % user.id)
    email, pas = Post.create_mailbox(user.id)
    user.email = email
    user.password = pas
    db.session.commit()
    dct = {
        "id": user.id
    }
    return ok(dct)


@bots.route('/get/user/<id>', methods=['POST'])
def get_user(user_id):
    # logging.info("")
    db = current_app.config["database"]
    query = db.session.query(User).\
        filter(User.id == user_id)
    user = query.first()
    if user:
        dct = {
            "id": user.id,
            "firstname": user.name,
            "surname": user.surname,
            "patronymic": user.patronymic
        }
        return ok(dct)
    else:
        return error("User id %s not found" % user_id)


@bots.route("/user/<int:user_id>/fnp/",
            methods=['POST'])
def change_user_firstname(user_id):
    db = current_app.config["database"]
    user = db.session.query(User).filter(User.id == user_id).first()
    if user:
        data = request.get_json()
        user.name = data["firstname"]
        user.surname = data["name"]
        user.patronymic = data["patronymic"]
        db.session.commit()
        return ok()
    return error()


@bots.route("/get/request/user/<int:user_id>/list/", methods=["POST"])
def get_list_requests(user_id):
    db = current_app.config["database"]
    reqs = db.session.query(Request, RequestStatus).\
        join(RequestStatus, Request.request_status_id == RequestStatus.id). \
        filter(Request.user_id == user_id). \
        filter(Request.date.isnot(None)). \
        options(
            Load(Request).load_only(
                "id",
                "date",
                "telegraph"
            ),
            Load(RequestStatus).load_only(
                "text"
            )
        )
    res = []
    for req, status in reqs:
        dct = {
            "id": req.id,
            "date": req.date,
            "telegraph": req.telegraph,
            "status": status.text
        }
        res.append(dct)
    return ok(res)


@bots.route("/create/request/<int:user_id>", methods=["POST"])
def create_request(user_id):
    db = current_app.config["database"]
    user = db.session.query(User).filter(User.id == user_id).first()
    if user:
        req = Request(user_id=user_id)
        db.session.add(req)
        db.session.commit()
        db.session.refresh(req)
        return ok({
            "id": req.id
        })
    return error("User %s does not exist" % user_id)


# curl -X POST localhost:5000/api/bot/request/5/update/ \
# -H "Content-Type: application/json" \
# -d '{"coordinate":{"latitude": "54.719441","longitude": "55.985409"}}'
@bots.route("/request/<int:request_id>/update/", methods=["POST"])
def update_request(request_id):
    db = current_app.config["database"]
    req = db.session.query(Request).filter(Request.id == request_id).first()
    if req:
        changes = False
        args = request.get_json()
        if args:
            if "problem" in args:
                changes = True
                problem = db.session.query(Problem).\
                    filter(Problem.name == args["problem"]).first()
                if not problem:
                    return error("Undefined problem type")
                req.problem_id = problem.id
            if "coordinate" in args and isinstance(args["coordinate"], dict):
                changes = True
                coordinates = args["coordinate"]
                if "latitude" in coordinates and "longitude" in coordinates:
                    latitude = coordinates["latitude"]
                    longitude = coordinates["longitude"]
                    try:
                        float(longitude); float(latitude)
                    except ValueError:
                        return error('Wrong coordinates')
                    geo_point = 'POINT(%s %s)' % (longitude, latitude)
                    req.coordinate = WKTElement(geo_point, srid=4326)
                else:
                    return error('Wrong coordinates')
            if "photo" in args:
                changes = True
                # TODO: how?
                pass
        if changes:
            req.date = datetime.now().date()
            db.session.commit()
            return ok()
        return error("Nothing to update")
    return error("Request %s does not exist" % request_id)


# curl -X POST localhost:5000/api/bot/request/5/request/ \
# -H "Content-Type: application/json" -d @test.json
@bots.route("/request/<int:request_id>/request/", methods=["POST"])
def action_request(request_id):
    form = request.get_json()
    logging.error(form)
    db = current_app.config["database"]
    req = db.session.query(Request).filter(Request.id == request_id).first()
    if req:
        if req.date:
            return error("Request is already sent")
        empty_req_fields = []
        if req.coordinate is None:
            empty_req_fields.append("coordinate")
        if not req.problem_id:
            empty_req_fields.append("problem")
        user = db.session.query(User).\
            filter(User.id == req.user_id).first()
        empty_user_fields = []
        if not user.name:
            empty_user_fields.append("firstname")
        if not user.surname:
            empty_user_fields.append("surname")
        if empty_req_fields or empty_user_fields:
            return error({
                "blank":{
                    "user": empty_user_fields,
                    "request": empty_req_fields
                }
            })
        else:
            problem = db.session.query(Problem). \
                filter(Problem.id == req.problem_id).first()
            complaint = Complaint(req, problem)
            if form and 'captcha_word' in form and 'captcha_code' in form:
                complaint.continue_init()
                data = complaint.get_data()
                appeal_data = {
                    "firstname": user.name,
                    "lastname": user.surname,
                    "pathronymic": user.patronymic,
                    "email": user.email,
                    "mailto": user.email,
                }
                appeal = create_appeal(complaint.procuracy.id)
                sendable = appeal.send_appeal(appeal_data)
                GenStatement.make_pdf(data, sendable)
                req.area_id = complaint.area.id
                # TODO: С реквест id могут быть проблемы (т.к id это sequence)
                req.request_status_id = 2
                req.date = datetime.now().date()
                db.session.commit()
                return ok()
            else:
                appeal = create_appeal(complaint.procuracy.id)
                captcha = appeal.captcha()
                return ok({'captcha': captcha})
    return error("Request %s does not exist" % request_id)


@bots.route("/request/<int:request_id>/link/", methods=["POST"])
def get_telegrapher_link(request_id):
    form = request.get_json()
    logging.error(form)
    db = current_app.config["database"]
    req = db.session.query(Request).filter(Request.id == request_id).first()
    if req:
        # Проверить, что все поля заполнены
        empty_req_fields = []
        if req.coordinate is None:
            empty_req_fields.append("coordinate")
        if not req.problem_id:
            empty_req_fields.append("problem")
        user = db.session.query(User).\
                    filter(User.id == req.user_id).first()
        empty_user_fields = []
        if not user.name:
            empty_user_fields.append("firstname")
        if not user.surname:
            empty_user_fields.append("surname")
        if empty_req_fields or empty_user_fields:
            return error({
                "blank":{
                    "user": empty_user_fields,
                    "request": empty_req_fields
                }
            })
        else:
            problem = db.session.query(Problem).\
                filter(Problem.id == req.problem_id).first()
            complaint = Complaint(req, problem)
            complaint.continue_init()
            data = complaint.get_data()
            link = GenStatement.create_preview(data, req.id)
            req.telegraph = link
            # TODO: С реквест id могут быть проблемы (т.к id это sequence)
            req.request_status_id = 1
            db.session.commit()
            return ok({"link": link})
    return error("Request %s does not exist" % request_id)



@bots.route("/get/problemtype/list", methods=["POST"])
def get_problemtype_list():
    db = current_app.config["database"]
    problems = db.session.query(ProblemType)
    resp = []
    for problem in problems:
        resp.append(problem.text)
    return ok(resp)


@bots.route("/get/problem/list", methods=["POST"])
def get_problem_list():
    form = request.get_json()
    logging.info("/get/problem/list/")
    logging.info("It is received data: ".format(form))
    if form:
        if 'problemtype' in form:
            problem_type = form["problemtype"]
            db = current_app.config["database"]
            problems = db.session.query(Problem, ProblemType).\
                join(ProblemType, Problem.problem_type_id == ProblemType.id).\
                filter(ProblemType.text == problem_type)
            resp = []
            for problem, _ in problems:
                resp.append(problem.name)
            return ok(resp)
    return error("Empty problem")


@bots.route("/test/<int:problem_id>/<int:request_id>", methods=["GET", "POST"])
def test(problem_id, request_id):
    logging.info("/test")
    # Уфа, наличия грязи, мусора на проезжей части
    db = current_app.config["database"]
    problem = db.session.query(Problem).\
        filter(Problem.id == problem_id).first()
    req = db.session.query(Request). \
        filter(Request.id == request_id).first()
    logging.info("Got problem")
    complaint = Complaint(req, problem)
    complaint.continue_init()
    logging.info("Complaint saved")
    data = complaint.get_data()
    logging.info("Complaint generated")
    return ok(data)


@bots.route("/ping", methods=["GET", "POST", "PUT", "DELETE"])
def ping():
    return ok()


@bots.errorhandler(404)
def not_found():
    return error("Method not allowed")


@bots.errorhandler(500)
def internal_error():
    return error("Internal server error")
