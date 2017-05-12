from flask import current_app, Blueprint, jsonify
from flask import request
from sqlalchemy.orm import Load
from Server.database.orm import User, Request, Status
from sqlalchemy.sql.expression import insert

from Server.api import view

api = Blueprint('api', __name__)


def ok(data=None):
    resp = {
        "status": "ok"
    }
    if data:
        resp.update("data", data)
    return jsonify(resp)


def error():
    resp = {
        "status": "error"
    }
    return jsonify(resp)


@api.route('/createuser', methods=['POST'])
def create_user():
    db = current_app.config["database"]
    user = User()
    db.session.add(user)
    db.session.commit()
    db.session.refresh(user)
    dct = {
        "id": user.id
    }
    return ok(dct)


@api.route("/user/<user_id>/firstname/<firstname>/",
           methods=['POST'])
def change_user_firstname(user_id, firstname):
    db = current_app.config["database"]
    user = db.session.query(User).filter(User.id == user_id).first()
    if user:
        user.name = firstname
        db.session.commit()
        return ok()
    return error()


@api.route("/user/<user_id>/surname/<surname>/",
           methods=['POST'])
def change_user_lastname(user_id, surname):
    db = current_app.config["database"]
    user = db.session.query(User).filter(User.id == user_id).first()
    if user:
        user.lastname = surname
        db.session.commit()
        return ok()
    return error()


@api.route("/request/user/<user_id>/list/")
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
