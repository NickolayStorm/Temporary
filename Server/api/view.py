from flask import jsonify


def ok(data=None):
    resp = {
        "status": "ok"
    }
    if data != None:
        resp["data"] = data
    return jsonify(resp)


def error(data=None):
    resp = {
        "status": "error"
    }
    if data != None:
        resp.update("data", data)
    return jsonify(resp)