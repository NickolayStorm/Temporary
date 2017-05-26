from flask import current_app, Blueprint, request
from sqlalchemy.orm import Load

from Server.api.orm import User, Request, \
    RequestStatus, ProblemType, Problem
from Server.api.view import ok, error
from Server.post import post

from Server.GenStatement.find_data import Complaint

bots = Blueprint('bot', __name__)


@bots.route('/create/user', methods=['POST'])
def create_user():
    db = current_app.config["database"]
    user = User()
    db.session.add(user)
    db.session.commit()
    db.session.refresh(user)
    print("Created user id(%s)" % user.id)
    email, pas = post.create_mailbox(user.id)
    user.email = email
    user.password = pas
    db.session.commit()
    dct = {
        "id": user.id
    }
    return ok(dct)


@bots.route('/get/user/<id>', methods=['POST'])
def get_user(id):
    db = current_app.config["database"]
    query = db.query.select(User).\
        filter(User.id == id)
    user = query.user
    if user:
        dct = {
            "id": user.id,
            "firstname": user.firstname,
            "surname": user.surname,
            "patronymic": user.patronymic
        }
        return ok(dct)
    else:
        return error("User id %s not found" % id)


@bots.route("/user/<int:user_id>/firstname/<firstname>/",
            methods=['POST'])
def change_user_firstname(user_id, firstname):
    db = current_app.config["database"]
    user = db.session.query(User).filter(User.id == user_id).first()
    if user:
        user.name = firstname
        db.session.commit()
        return ok()
    return error()


@bots.route("/user/<int:user_id>/surname/<surname>/",
            methods=['POST'])
def change_user_lastname(user_id, surname):
    db = current_app.config["database"]
    user = db.session.query(User).filter(User.id == user_id).first()
    if user:
        user.lastname = surname
        db.session.commit()
        return ok()
    return error()


@bots.route("/get/request/user/<int:user_id>/list/", methods=["POST"])
def get_list_requests(user_id):
    db = current_app.config["database"]
    # TODO: Не работает (ошибка в join)
    reqs = db.session.query(Request, RequestStatus).\
        filter(Request.user_id == user_id).\
        join(Request.request_status_id == RequestStatus.id).\
        options(
            Load(Request).load_only(
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
            "date": req.date,
            "telegraph": req.telegraph,
            "status": status.typename
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


@bots.route("/request/<int:request_id>/update/", methods=["POST"])
def update_request(request_id):
    db = current_app.config["database"]
    req = db.session.query(Request).filter(Request.id == request_id).first()
    if req:
        args = request.form
        # TODO: find all args and push it to db
        # id = Column(Integer, primary_key=True) - есть
        # user_id = Column(Integer) - есть
        # date = Column(TIMESTAMP) - в /request/<id>/request/
        # photo_path = Column(String) - сгенерировать, для этого достать фото
        # coordinate = Column(Geometry('POINT')) - прочитать
        # telegraph = Column(String) - в /request/<id>/request/
        # area_id = Column(Integer) - в /request/<id>/request/
        # request_status_id = Column(Integer) - /request/<id>/request/
        # problem_id = Column(Integer) - выяснили (ниже)
        # TODO: rewrite problem
        # if "problem_type" in args:
        #     problem = db.session.query(ProblemType).\
        #         filter(ProblemType.text == args["problem_type"]).first()
        #     if not problem:
        #         return error("Undefined problem type")
        #     problem_id = problem.id
        if "coordinate" in args:
            coordinate = args["coordinate"]
            """
                TODO: read coordinates; handle errors; etc.
            """
        if "photo" in args:
            # TODO: how?
            pass
        return ok()
    return error("Request %s does not exist" % request_id)


@bots.route("/request/<int:request_id>/request/", methods=["POST"])
def action_request(request_id):
    db = current_app.config["database"]
    req = db.session.query(Request).filter(Request.id == request_id).first()
    if req:
        # Проверить, что все поля заполнены
        empty_req_fields = []
        if not req.coordinate:
            empty_req_fields.append("coordinate")
        if not req.problem_id:
            empty_req_fields.append("problem_type")
        if not req.photo_path:
            empty_req_fields.append("photo")
        user = db.session.query(User).filter(User.id == req.user_id)
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
            """
                TODO: captcha on site
            """
            # complaint = Complaint(request_id, problem)
            # site = complaint.site
            # If captcha in site -> return captcha
            # else: Complaint().continue_init().compile()
            # and then
            """
             TODO: create all stuff for request
                   and return captcha link
                   fill following fields:
                       date = Column(TIMESTAMP)
                       telegraph = Column(String)
                       area_id = Column(Integer)
                       request_status_id = Column(Integer)
            """
            return ok()
    return error("Request %s does not exist" % request_id)


@bots.route("/get/problemtype/list", methods=["POST"])
def get_problem_list():
    db = current_app.config["database"]
    problems = db.session.query(ProblemType)
    resp = []
    for problem in problems:
        resp.append(problem.text)
    return ok(resp)


@bots.route("/get/problem/<int:type>/list", methods=["POST"])
def get_problem_list(type):
    db = current_app.config["database"]
    problems = db.session.query(Problem).\
        filter(Problem.problem_type_id == type)
    resp = []
    for problem in problems:
        resp.append(problem.text)
    return ok(resp)


@bots.route("/request/<int:request_id>/captcha/<transcript>", methods=["POST"])
def get_captcha_transcript(transcript):
    # Какие-то токены для капчи?
    # TODO: make request
    # TODO: return not ok
    return ok()


@bots.route("", methods=["GET", "POST"])
def test():
    # Уфа, наличия грязи, мусора на проезжей части
    db = current_app.config["database"]
    problem = db.session.query(Problem).\
        filter(Problem.id == 2).first()
    complaint = Complaint(4, problem)
    complaint.continue_init()
    complaint.compile()
    return ok()


@bots.errorhandler(404)
def not_found():
    return error("Method not allowed")


@bots.errorhandler(500)
def internal_error():
    return error("Internal server error")
