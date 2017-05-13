from flask import current_app, Blueprint, request
from sqlalchemy.orm import Load

from Server.api.view import ok, error
from Server.database.orm import User, Request, Status

bots = Blueprint('bot', __name__)


@bots.route('/create/user', methods=['POST'])
def create_user():
    db = current_app.config["database"]
    user = User()
    db.session.add(user)
    db.session.commit()
    db.session.refresh(user)
    print("Created user id(%s)" % user.id)
    dct = {
        "id": user.id
    }
    return ok(dct)


@bots.route("/user/<user_id>/firstname/<firstname>/",
            methods=['POST'])
def change_user_firstname(user_id, firstname):
    db = current_app.config["database"]
    user = db.session.query(User).filter(User.id == user_id).first()
    if user:
        user.name = firstname
        db.session.commit()
        return ok()
    return error()


@bots.route("/user/<user_id>/surname/<surname>/",
            methods=['POST'])
def change_user_lastname(user_id, surname):
    db = current_app.config["database"]
    user = db.session.query(User).filter(User.id == user_id).first()
    if user:
        user.lastname = surname
        db.session.commit()
        return ok()
    return error()


@bots.route("/get/request/user/<user_id>/list/")
def get_list_requests(user_id):
    db = current_app.config["database"]
    reqs = db.session.query(Request, Status).\
        filter(Request.user_id == user_id).\
        join(Request.status_id == Status.id).\
        options(
            Load(Request).load_only(
                "date",
                "telegraph"
            ),
            Load(Status).load_only(
                "typename"
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


@bots.route("/create/request/<user_id>", methods=["POST"])
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


@bots.route("/request/<request_id>/update/")
def update_request(request_id):
    db = current_app.config["database"]
    req = db.session.query(Request).filter(Request.id == request_id).first()
    if req:
        args = request.form
        # TODO: args
        coordinates = args["cooridnate"]
        # TODO: Find out category
        # category_id = args["category"]
        return ok()
    return error("Request %s does not exist" % request_id)


@bots.route("/request/<request_id>/request/")
def action_request(request_id):
    db = current_app.config["database"]
    req = db.session.query(Request).filter(Request.id == request_id).first()
    if req:
        # Проверить, что все поля заполнены
        empty_req_fields = []
        if not req.coordinate:
            empty_req_fields.append("coordinate")
        if not req.category_id:
            empty_req_fields.append("category")
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
            # TODO: make_request
            return ok()
    return error("Request %s does not exist" % request_id)


@bots.errorhandler(404)
def not_found():
    return error("Method not allowed")

@bots.errorhandler(500)
def not_found():
    return error("Internal server error")
