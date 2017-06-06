import requests
import string
import random
import time
import logging
from Server.api.orm import User
from flask import current_app

def create_mailbox(user_id):  #, address, session):
    time.sleep(2)
    return "mylogin", "mypassword"
    # for i in range(5):
    #     time.sleep(1)
    #     logging.error("In loop")
    #     logging.error("With context")
    #     login = "user" + str(user_id)
    #     password = ''.join(random.choice(string.ascii_uppercase) for _ in range(10))
    #     u = User(id = user_id, email='our_mail')
    #     session.merge(u)
    # TODO: test and make error handling also request response
    # r = requests.post(address + "/addbox", json={
    #     "login": login,
    #     "password": password
    # })
    # dct = r.json()
    # # Success: ("ok" | "error")
    # success = dct.get("success", "success")
    # if success == "ok":
    #     print("Created mailbox login {} password {}".format(login, password))
    #     # Edit box
    #     r = requests.post(address + "/editbox", json={
    #         "login": login,
    #         "iname": "user%s" % user_id
    #     })
    #     # TODO: check if updated
    #     return login, password
    # return None, None
