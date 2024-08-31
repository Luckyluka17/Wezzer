import requests
from flask import Blueprint, render_template, request, make_response, redirect
import json
from main import *
from lib.proxy import *

with open("config.yml", "r", encoding="utf-8") as f:
    config_file = yaml.safe_load(f)
    f.close()

location = Blueprint("location", __name__)

@location.route("/search_city", methods=["GET"])
def search_city():
    geocoding_data = fetch_data(f"https://geocoding-api.open-meteo.com/v1/search?name={request.args.get('city')}&count=20&language=fr&format=json", config_file)

    if geocoding_data.get("results") == None:
        geocoding_data["results"] = []

    additional_results = fetch_data(f"https://geocoding-api.open-meteo.com/v1/search?name={request.args.get('city').replace(' ', '-')}&count=20&language=fr&format=json", config_file)

    if additional_results.get("results") == None:
        additional_results["results"] = []

    for result in additional_results["results"]:
        geocoding_data["results"].append(result)

    resp = make_response(render_template(
        "results.html",
        data=geocoding_data, 
        n=len(geocoding_data["results"])
    ))

    return resp


@location.route("/set_location", methods=["GET"])
def set_location():
    resp = make_response(redirect("/"))

    raw = {
        "cityname": request.args.get('cityname'),
        "location": [float(request.args.get('latitude')), float(request.args.get('longitude'))],
        "country": request.args.get('country')
    }

    resp.set_cookie("loc", json.dumps(raw), httponly=True, secure=True, samesite='Strict')

    return resp