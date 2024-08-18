from flask import Blueprint, make_response, redirect

settings = Blueprint("settings", __name__)

@settings.route("/delete_cookies")
def delete_cookies():
    resp = make_response(redirect("/"))

    resp.set_cookie('loc', '', expires=0)
    resp.set_cookie('settings', '', expires=0)

    return resp