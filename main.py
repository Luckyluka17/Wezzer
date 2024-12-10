from datetime import datetime, timedelta
import io
import json
import os

import feedparser
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import yaml
from flask import Flask, make_response, redirect, render_template, request, send_file

from lib.filters import filters
from lib.location import location
from lib.proxy import *
from lib.settings import settings

app = Flask(__name__)

with open("/data/config.yml", "r", encoding="utf-8") as f:
    config_file = yaml.safe_load(f)
    f.close()

# Ajouter tous les blueprints
app.register_blueprint(location)
app.register_blueprint(settings)
app.register_blueprint(filters)

def api_link(location_cookie):

    latitude, longitude = json.loads(location_cookie)["location"]

    base_url = f"https://{config_file['api']}/v1/forecast?latitude={latitude}&longitude={longitude}&timezone=auto"
    basic = f"{base_url}&current=temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,rain,surface_pressure,wind_speed_10m,wind_direction_10m&minutely_15=relative_humidity_2m,rain,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation_probability,rain,surface_pressure,cloud_cover_mid,wind_speed_10m,wind_direction_10m,uv_index,is_day,direct_radiation,snowfall&daily=temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,sunrise,sunset,uv_index_max,precipitation_hours,precipitation_probability_max,precipitation_sum"
    past = f"{base_url}&hourly=temperature_2m,relative_humidity_2m,rain,direct_radiation&past_days=1&forecast_days=1"
    air_quality = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={latitude}&longitude={longitude}&current=european_aqi&forecast_days=1"

    return basic, past, air_quality


@app.route("/")
def index():
    location_cookie = request.cookies.get("loc")

    # Charger le flux RSS
    notifications = feedparser.parse(config_file["rss"])

    if location_cookie == None:
        return redirect("/welcome")
    else:
        url_basic, url_past, url_air = api_link(location_cookie)
        
        data_basic = fetch_data(url_basic, config_file)
        data_past = fetch_data(url_past, config_file)
        data_air = fetch_data(url_air, config_file)

        date = data_basic["current"]["time"].replace("-", "/").split("T")[0].split("/")
        date = f"{date[2]}/{date[1]}/{date[0]}"

        data_basic["is_december"] = True if str(data_basic["current"]["time"].replace("-", "/").split("T")[0].split("/")[1]) == "12" else False

        time = int(data_basic["current"]["time"].replace("-", "/").split("T")[1].split(":")[0])

        for t in range(1,7):
            data_basic["daily"]["time"][t] = data_basic["daily"]["time"][t].replace("-", "/").split("T")[0].split("/")
            data_basic["daily"]["time"][t] = f"{data_basic['daily']['time'][t][2]}/{data_basic['daily']['time'][t][1]}/{data_basic['daily']['time'][t][0]}"

        tmp1 = []
        for i in range(time+25,time, -1):
            if i-25-time+1 < 0:
                tmp1.append(int(data_past["hourly"]["direct_radiation"][i]))

        tmp2 = []
        for i in range(time+25,time, -1):
            if i-25-time+1 < 0:
                tmp2.append(int(data_past["hourly"]["rain"][i]))

        tmp3 = []
        for i in range(time+25,time, -1):
            if i-25-time+1 < 0:
                tmp3.append(int(data_past["hourly"]["relative_humidity_2m"][i]))

        past_total = [
            sum(tmp1),
            sum(tmp2),
            round(np.mean(tmp3), 1)
        ]


        for i in range(0, len(data_basic["hourly"]["snowfall"])):
            data_basic["hourly"]["snowfall"][i] = int(data_basic["hourly"]["snowfall"][i]*10) # Convertir en mm

        for i in range(0, len(data_basic["hourly"]["direct_radiation"])):
            data_basic["hourly"]["direct_radiation"][i] = int(round(data_basic["hourly"]["direct_radiation"][i], 0))


        # Obtenir les phases lunaire
        moonphase = []
        for i in range(0, 8):
            day_timestamp = int((datetime.now() + timedelta(days=i)).timestamp())

            with requests.get(f"https://api.farmsense.net/v1/moonphases/?d={day_timestamp}") as r:
                moon_api = json.loads(r.text)[0]
                r.close()
            
            if moon_api["Phase"] == "New Moon":
                moonphase.append(["Nouvelle Lune", "🌑"])
            elif moon_api["Phase"] == "Waxing Crescent":
                moonphase.append(["Premier Croissant", "🌒"])
            elif moon_api["Phase"] == "First Quarter":
                moonphase.append(["Premier Quartier", "🌓"])
            elif moon_api["Phase"] == "Waxing Gibbous":
                moonphase.append(["Lune gibbeuse croissante", "🌔"])
            elif moon_api["Phase"] == "Full Moon":
                moonphase.append(["Pleine Lune", "🌕"])
            elif moon_api["Phase"] == "Waning Gibbous":
                moonphase.append(["Lune gibbeuse décroissante", "🌖"])
            elif moon_api["Phase"] == "Last Quarter":
                moonphase.append(["Dernier Quartier", "🌗"])
            elif moon_api["Phase"] == "Waning Crescent":
                moonphase.append(["Dernier Croissant", "🌘"])

            moonphase[i].append(round(moon_api["Age"], 1))
            moonphase[i].append(moon_api["Illumination"]*100)
            moonphase[i].append(datetime.fromtimestamp(day_timestamp).strftime("%d/%m/%Y"))

    response = make_response(
        render_template(
            "app.html",
            date=date,
            raw=data_basic,
            time=time,
            loc=json.loads(request.cookies.get("loc")),
            config_file=config_file,
            raw_past=data_past,
            raw_air=data_air,
            past_total=past_total,
            notifications=notifications.entries,
            moon_phase=moonphase,
        )
    )
    
    if not request.cookies.get("settings"):
        response.set_cookie("settings", json.dumps({"solar_radiation": True, "graphs": True}), httponly=True, secure=True, samesite='Strict')

    return response

@app.route("/welcome")
def welcome():

    if request.cookies.get("loc") != None:
        return redirect("/")

    response = make_response(
        render_template("welcome.html")
    )

    return response

@app.route("/graph")
def basic_graph():
                        
    plt.switch_backend('Agg')

    location_cookie = request.cookies.get("loc")
    url_basic, url_past, url_air = api_link(location_cookie)
    data_weather = fetch_data(url_basic, config_file)

    setting_name = request.args.get("dtg")

    hours = []
    data = []

    for v in range(0, 97):
        data.append(data_weather["minutely_15"][setting_name][v])

    for h in range(0, 97):
        hours.append(data_weather["minutely_15"]["time"][h].split("T")[1])

    df = pd.DataFrame({'Temps': hours, f"{setting_name}": data})

    df = df.drop_duplicates(subset=['Temps'])
    df = df.sort_values(by='Temps')

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(df['Temps'], df[setting_name], marker='o', linestyle='-', color='b', label=setting_name)


    ax.legend()

    ax.set_xlabel('Temps (24h)')
    ax.set_ylabel(f"{setting_name} (Unité: {data_weather['hourly_units'][setting_name]})")

    
    plt.xticks(rotation=45)

    ax.set_xticks(ax.get_xticks()[::4])
    plt.tight_layout()

    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)

    plt.close(fig)

    return send_file(img, mimetype='image/png')

# Pages d'erreur
@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", error_code=404), 404

@app.errorhandler(500)
def error(error):
    return render_template("error.html", error_code=500), 500

def init():
    return app