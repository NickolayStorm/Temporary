import logging

from datetime import datetime
from flask import current_app, Blueprint, request
from sqlalchemy.orm import Load
from Server.api.orm import User, Request, \
    RequestStatus, ProblemType, Problem
from geoalchemy2.elements import WKTElement
from Server.api.view import ok, error
# from Server.post import post
from Server.AppealScripts.create_appeal import create_appeal

from Server.GenStatement.find_data import Complaint

bots = Blueprint('bot', __name__)


@bots.route('/create/user', methods=['POST'])
def create_user():
    logging.error("/create/user")
    db = current_app.config["database"]
    user = User()
    db.session.add(user)
    db.session.commit()
    db.session.refresh(user)
    logging.error("refreshed")
    logging.error("Created user id(%s)" % user.id)
    # email, pas = post.create_mailbox(user.id)
    # user.email = email
    # user.password = pas
    # print("mailbox created")
    db.session.commit()
    dct = {
        "id": user.id
    }
    logging.error("commited")
    return ok(dct)


@bots.route('/get/user/<id>', methods=['POST'])
def get_user(id):
    # logging.error("")
    db = current_app.config["database"]
    query = db.session.query(User).\
        filter(User.id == id)
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
        return error("User id %s not found" % id)


@bots.route("/user/<int:user_id>/fnp/",
            methods=['POST'])
def change_user_firstname(user_id):
    db = current_app.config["database"]
    user = db.session.query(User).filter(User.id == user_id).first()
    if user:
        data = request.form
        user.name = data["firstname"]
        user.surname = data["name"]
        user.patronymic = data["patronymic"]
        db.session.commit()
        return ok()
    return error()


@bots.route("/get/request/user/<int:user_id>/list/", methods=["POST"])
def get_list_requests(user_id):
    db = current_app.config["database"]
    # TODO: join Request status
    reqs = db.session.query(Request).\
        filter(Request.user_id == user_id). \
        filter(Request.date.isnot(None)). \
        options(
            Load(Request).load_only(
                "id",
                "date",
                "telegraph"
            )
            # Load(RequestStatus).load_only(
            #     "text"
            # )
        )
    res = []
    for req in reqs:
        dct = {
            "date": req.date,
            "telegraph": req.telegraph
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
        args = request.form  # get_json()
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
            db.session.commit()
            return ok()
        return error("Nothing to update")
    return error("Request %s does not exist" % request_id)


# curl -X POST localhost:5000/api/bot/request/5/request/ \
# -H "Content-Type: application/json" -d @test.json
@bots.route("/request/<int:request_id>/request/", methods=["POST"])
def action_request(request_id):
    form = request.get_json()
    db = current_app.config["database"]
    req = db.session.query(Request).filter(Request.id == request_id).first()
    if req:
        if req.date:
            return error("Request is already sent")
        # Проверить, что все поля заполнены
        empty_req_fields = []
        # TODO: TypeError("Boolean value of this clause is not defined")
        # if req.coordinate == None:
        #     empty_req_fields.append("coordinate")
        # if not req.problem_id:
        #     empty_req_fields.append("problem")
        # if not req.photo_path:
        #     empty_req_fields.append("photo")
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
            if 'captcha_word' in form and 'captcha_code' in form:
                problem = db.session.query(Problem).\
                    filter(Problem.id == req.problem_id).first()
                complaint = Complaint(request_id, problem)
                complaint.continue_init()
                data = complaint.get_data()
                # TODO: compile data with coords etc -> text
                text = ''
                # TODO: Telegrapher -> telegraph
                telegraph = ''
                req.telegraph = telegraph
                req.area_id = complaint.area.id
                # TODO: req.request_status_id
                # TODO: coordinates to appeal
                appeal_data = {
                    "firstname": user.name,
                    "lastname": user.surname,
                    "pathronymic": user.patronymic,
                    "email": user.email,
                    "mailto": user.email,
                }
                appeal = create_appeal(complaint.procuracy.id)
                appeal.send_appeal(appeal_data)
                req.date = datetime.now().date()
                db.session.commit()
                return ok()
            else:
                problem = db.session.query(Problem). \
                    filter(Problem.id == req.problem_id).filter()
                complaint = Complaint(request_id, problem)
                appeal = create_appeal(complaint.procuracy.id)
                captcha = appeal.captcha()
                return ok({'captcha': captcha})
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
    form = request.form  # get_json()
    logging.error("/get/problem/list/")
    logging.error("It is received data: ".format(form))
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


@bots.route("/test/<int:problem_id>", methods=["GET", "POST"])
def test(problem_id):
    logging.error("/test")
    # Уфа, наличия грязи, мусора на проезжей части
    db = current_app.config["database"]
    problem = db.session.query(Problem).\
        filter(Problem.id == problem_id).first()
    logging.error("Got problem")
    complaint = Complaint(4, problem)
    complaint.continue_init()
    logging.error("Complaint saved")
    data = complaint.get_data()
    logging.error("Complaint generated")
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
