from flask import jsonify


def ok(data=None):
    resp = {
        "status": "ok"
    }
    if data:
        resp["data"] = data
    return jsonify(resp)


def error(data=None):
    resp = {
        "status": "error"
    }
    if data:
        resp.update("data", data)
    return jsonify(resp)