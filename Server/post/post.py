import requests
import string
import random
from flask import current_app


def create_mailbox(user_id):
    address = current_app.config["POST_ADDRESS"]
    login = "user" + str(user_id)
    password = ''.join(random.choice(string.ascii_uppercase) for _ in range(10))
    # TODO: test and make error handling also request response
    r = requests.post(address + "/addbox", json={
        "login": login,
        "password": password
    })
    dct = r.json()
    # Success: ("ok" | "error")
    success = dct.get("success", "success")
    if success == "ok":
        print("Created mailbox login {} password {}".format(login, password))
        # Edit box
        r = requests.post(address + "/editbox", json={
            "login": login,
            "iname": "user%s" % user_id
        })
        # TODO: check if updated
        return login, password
    return None, None
