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
    print("/create/user")
    db = current_app.config["database"]
    user = User()
    db.session.add(user)
    db.session.commit()
    db.session.refresh(user)
    print("refreshed")
    print("Created user id(%s)" % user.id)
    # email, pas = post.create_mailbox(user.id)
    # user.email = email
    # user.password = pas
    # print("mailbox created")
    db.session.commit()
    dct = {
        "id": user.id
    }
    print("commited")
    return ok(dct)


@bots.route('/get/user/<id>', methods=['POST'])
def get_user(id):
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
    # TODO: Не работает (ошибка в join)
    reqs = db.session.query(Request, RequestStatus).\
        filter(Request.user_id == user_id).\
        join(RequestStatus, Request.request_status_id == RequestStatus.id).\
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
            "id": Request.id,
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
        # if "problem" in args:
        #     problem = db.session.query(Problem).\
        #         filter(Problem.text == args["problem_type"]).first()
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
def get_problemtype_list():
    db = current_app.config["database"]
    problems = db.session.query(ProblemType)
    resp = []
    for problem in problems:
        resp.append(problem.text)
    return ok(resp)


@bots.route("/get/problem/list", methods=["POST"])
def get_problem_list():
    form = request.form
    print(form)
    problem_type = form["problemtype"]
    db = current_app.config["database"]
    problems = db.session.query(Problem, ProblemType).\
        join(ProblemType, Problem.problem_type_id == ProblemType.id).\
        filter(ProblemType.text == problem_type)
    resp = []
    for problem, _ in problems:
        resp.append(problem.text)
    return ok(resp)


@bots.route("/request/<int:request_id>/captcha/<transcript>", methods=["POST"])
def get_captcha_transcript(transcript):
    # Какие-то токены для капчи?
    # TODO: make request
    # TODO: return not ok
    return ok()


@bots.route("/test/<int:problem_id>", methods=["GET", "POST"])
def test(problem_id):
    print("/test")
    # Уфа, наличия грязи, мусора на проезжей части
    db = current_app.config["database"]
    problem = db.session.query(Problem).\
        filter(Problem.id == problem_id).first()
    print("Got problem")
    complaint = Complaint(4, problem)
    complaint.continue_init()
    print("Complaint saved")
    data = complaint.compile()
    print("Complaint generated")
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
