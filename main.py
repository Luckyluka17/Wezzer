from flask import request, render_template, jsonify, Flask, redirect, send_file, make_response
import json
import os
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import yaml
import random

# Créer l'application
app = Flask(__name__)

version = "0.2"

plt.switch_backend('Agg')

with open("config.yml", "r", encoding="utf-8") as f:
    config_file = yaml.safe_load(f)
    f.close()

def api_link(location_cookie):
    if location_cookie == None:
        url_api_weather = f"https://{config_file['api']}/v1/forecast?latitude=48.85538895024384&longitude=2.3505623992614475&current=temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,rain,surface_pressure,wind_speed_10m,wind_direction_10m&minutely_15=relative_humidity_2m,rain,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation_probability,rain,surface_pressure,cloud_cover,wind_speed_10m,wind_direction_10m,uv_index,is_day,direct_radiation&daily=temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,sunrise,sunset,uv_index_max,precipitation_hours,precipitation_probability_max&timezone=auto"
        url_api_weather_past = f"https://{config_file['api']}/v1/forecast?latitude=48.85538895024384&longitude=2.3505623992614475&hourly=temperature_2m,relative_humidity_2m,rain,direct_radiation&past_days=1&forecast_days=1"

    else:
        loc = json.loads(location_cookie)
        url_api_weather = f"https://{config_file['api']}/v1/forecast?latitude={loc['location'][0]}&longitude={loc['location'][1]}&current=temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,rain,surface_pressure,wind_speed_10m,wind_direction_10m&minutely_15=relative_humidity_2m,rain,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation_probability,rain,surface_pressure,cloud_cover,wind_speed_10m,wind_direction_10m,uv_index,is_day,direct_radiation&daily=temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,sunrise,sunset,uv_index_max,precipitation_hours,precipitation_probability_max&timezone=auto"
        url_api_weather_past = f"https://{config_file['api']}/v1/forecast?latitude={loc['location'][0]}&longitude={loc['location'][1]}&hourly=temperature_2m,relative_humidity_2m,rain,direct_radiation&past_days=1&forecast_days=1"

    return url_api_weather, url_api_weather_past

def random_proxy():
    with requests.get(f"https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout={config_file['proxy_max_timeout']}&country={config_file['proxy_country_code']}&ssl=all&anonymity=all") as r:
        proxies = r.text.split("\n")
        r.close()


    return str(random.choice(proxies))


@app.route("/")
def site():
    url_api_weather, url_api_weather_past = api_link(request.cookies.get("loc"))

    try:
        proxy_ip = random_proxy()

        with requests.get(f"http://ip-api.com/json/{proxy_ip.split(':')[0]}") as r:
            proxy = json.loads(r.text)
            r.close()
        
        with requests.get(url_api_weather, proxies={"http": random_proxy()}) as r:
            data_weather = json.loads(r.text)
            r.close()

        with requests.get(url_api_weather_past, proxies={"http": random_proxy()}) as r:
            data_weather_past = json.loads(r.text)
            r.close()
    except:
        proxy = {}

        with requests.get(url_api_weather) as r:
            data_weather = json.loads(r.text)
            r.close()

        with requests.get(url_api_weather) as r:
            data_weather_past = json.loads(r.text)
            r.close()


    # with requests.get(f"http://localhost:{config_file['port']}/static/feed.json") as r:
    #     notifications = json.loads(r.text)
    #     r.close()

    # notifications.reverse()

    date = data_weather["current"]["time"].replace("-", "/").split("T")[0].split("/")
    date = f"{date[2]}/{date[1]}/{date[0]}"

    time = int(data_weather["current"]["time"].replace("-", "/").split("T")[1].split(":")[0])

    for t in range(1,7):
        data_weather["daily"]["time"][t] = data_weather["daily"]["time"][t].replace("-", "/").split("T")[0].split("/")
        data_weather["daily"]["time"][t] = f"{data_weather['daily']['time'][t][2]}/{data_weather['daily']['time'][t][1]}/{data_weather['daily']['time'][t][0]}"

    tmp1 = []
    for i in range(time+25,time, -1):
        if i-25-time+1 < 0:
            tmp1.append(int(data_weather_past["hourly"]["direct_radiation"][i]))

    tmp2 = []
    for i in range(time+25,time, -1):
        if i-25-time+1 < 0:
            tmp2.append(int(data_weather_past["hourly"]["rain"][i]))

    tmp3 = []
    for i in range(time+25,time, -1):
        if i-25-time+1 < 0:
            tmp3.append(int(data_weather_past["hourly"]["relative_humidity_2m"][i]))

    past_total = [
        sum(tmp1),
        sum(tmp2),
        round(np.mean(tmp3), 1)
    ]

    if request.cookies.get("loc") == None:
        resp = make_response(render_template(
            "app.html",
            date=date,
            raw=data_weather,
            time=time,
            version=version,
            config_file=config_file,
            # notifications=notifications,
            raw_past=data_weather_past,
            proxy=proxy,
            past_total=past_total,
            loc=json.loads('{"cityname": "Paris", "location": [48.85538895024384, 2.3505623992614475], "country": "France"}'),
        ))
        resp.set_cookie("loc",  '{"cityname": "Paris", "location": [48.85538895024384, 2.3505623992614475], "country": "France"}')

        if request.cookies.get("settings") == None:
            resp.set_cookie("settings", json.dumps({"solar_radiation": True, "graphs": False}))
            
    else: 
        resp = make_response(render_template(
            "app.html",
            date=date,
            raw=data_weather,
            time=time,
            version=version,
            loc=json.loads(request.cookies.get("loc")),
            config_file=config_file,
            # notifications=notifications,
            raw_past=data_weather_past,
            proxy=proxy,
            past_total=past_total,
        ))

        if request.cookies.get("settings") == None:
            resp.set_cookie("settings", json.dumps({"solar_radiation": True, "graphs": False}))



    return resp


@app.route("/set_settings")
def set_settings():
    resp = make_response(redirect("/"))
    settings = {
        "solar_radiation": True,
        "graphs": False,
    }

    if request.args.get("sunstats") != None:
        settings["solar_radiation"] == True
    else:
        settings["solar_radiation"] == False

    if request.args.get("graphs") != None:
        settings["graphs"] == True
    else:
        settings["graphs"] == False


    resp.set_cookie("settings", json.dumps(settings))
    

    return resp

@app.route("/search_city", methods=["GET"])
def search_city():
    try:
        with requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={request.args.get('city')}&count=20&language=fr&format=json", proxies={"http": random_proxy()}) as r:
            geocoding_data = json.loads(r.text)
            r.close()
    except:
        with requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={request.args.get('city')}&count=20&language=fr&format=json") as r:
            geocoding_data = json.loads(r.text)
            r.close()

    if geocoding_data.get("results") == None:
        geocoding_data["results"] = []

    if " " in request.args.get('city'):
        try:
            with requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={request.args.get('city').replace(' ', '-')}&count=20&language=fr&format=json", proxies={"http": random_proxy()}) as r:
                additional_results = json.loads(r.text)
                r.close()

            if additional_results.get("results") == None:
                additional_results["results"] = []
        except:
            with requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={request.args.get('city').replace(' ', '-')}&count=20&language=fr&format=json") as r:
                additional_results = json.loads(r.text)
                r.close()

            if additional_results.get("results") == None:
                additional_results["results"] = []

        for result in additional_results["results"]:
            geocoding_data["results"].append(result)

    resp = make_response(render_template(
        "results.html",
        data=geocoding_data, 
        n=len(geocoding_data["results"]),
        version=version
    ))

    return resp


@app.route("/set_location", methods=["GET"])
def set_location():
    resp = make_response(redirect("/"))

    raw = {
        "cityname": request.args.get('cityname'),
        "location": [float(request.args.get('latitude')), float(request.args.get('longitude'))],
        "country": request.args.get('country')
    }

    resp.set_cookie("loc", json.dumps(raw))

    return resp

@app.route("/delete_cookies")
def delete_cookies():
    resp = make_response(redirect("/"))

    resp.set_cookie('loc', '', expires=0)
    resp.set_cookie('settings', '', expires=0)

    return resp

@app.route("/graph/humidity.png")
def graph_humidity():
    url_api_weather, url_api_weather_past = api_link(request.cookies.get("loc"))
   
    with requests.get(url_api_weather) as r:
        data_weather = json.loads(r.text)
        r.close()


    hours = []
    humidity = []

    for v in range(0, 97):
        humidity.append(data_weather["minutely_15"]["relative_humidity_2m"][v])

    for h in range(0, 97):
        hours.append(data_weather["minutely_15"]["time"][h].split("T")[1])

    df = pd.DataFrame({'Temps': hours, 'Humidité': humidity})

    df = df.drop_duplicates(subset=['Temps'])
    df = df.sort_values(by='Temps')

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(df['Temps'], df['Humidité'], marker='o', linestyle='-', color='b', label='Humidité')


    ax.legend()

    ax.set_xlabel('Temps (24h)')
    ax.set_ylabel('Humidité (%)')

    
    plt.xticks(rotation=45)

    ax.set_xticks(ax.get_xticks()[::4])
    plt.tight_layout()

    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)

    plt.close(fig)

    return send_file(img, mimetype='image/png')

def generate_graph(route, ylabel, data_key):
    url_api_weather, _ = api_link(request.cookies.get("loc"))
    with requests.get(url_api_weather) as r:
        data_weather = r.json()

    times = [t.split("T")[1] for t in data_weather["minutely_15"]["time"][:97]]
    values = data_weather["minutely_15"][data_key][:97]

    df = pd.DataFrame({'Temps': times, ylabel: values}).drop_duplicates(subset=['Temps']).sort_values(by='Temps')

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df['Temps'], df[ylabel], marker='o', linestyle='-', color='b', label=ylabel)
    ax.legend()
    ax.set_xlabel('Temps (24h)')
    ax.set_ylabel(ylabel)
    plt.xticks(rotation=45)
    ax.set_xticks(ax.get_xticks()[::4])
    plt.tight_layout()

    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    plt.close(fig)

    return send_file(img, mimetype='image/png')



@app.route("/graph/rain.png")
def graph_rain():
    url_api_weather, url_api_weather_past = api_link(request.cookies.get("loc"))
        
    with requests.get(url_api_weather) as r:
        data_weather = json.loads(r.text)
        r.close()

    hours = []
    rain = []

    for v in range(0, 97):
        rain.append(data_weather["minutely_15"]["rain"][v])

    for h in range(0, 97):
        hours.append(data_weather["minutely_15"]["time"][h].split("T")[1])

    df = pd.DataFrame({'Temps': hours, 'Pluviométrie': rain})

    df = df.drop_duplicates(subset=['Temps'])
    df = df.sort_values(by='Temps')

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(df['Temps'], df['Pluviométrie'], marker='o', linestyle='-', color='b', label='Pluviométrie')


    ax.legend()

    ax.set_xlabel('Temps (24h)')
    ax.set_ylabel('Pluviométrie (mm)')

    
    plt.xticks(rotation=45)

    ax.set_xticks(ax.get_xticks()[::4])
    plt.tight_layout()

    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)

    plt.close(fig)

    return send_file(img, mimetype='image/png')



@app.route("/graph/wind.png")
def graph_wind():
    url_api_weather, url_api_weather_past = api_link(request.cookies.get("loc"))


    with requests.get(url_api_weather) as r:
        data_weather = json.loads(r.text)
        r.close()

    hours = []
    speed = []

    for v in range(0, 97):
        speed.append(data_weather["minutely_15"]["wind_speed_10m"][v])

    for h in range(0, 97):
        hours.append(data_weather["minutely_15"]["time"][h].split("T")[1])

    df = pd.DataFrame({'Temps': hours, 'Vitesse': speed})

    df = df.drop_duplicates(subset=['Temps'])
    df = df.sort_values(by='Temps')

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(df['Temps'], df['Vitesse'], marker='o', linestyle='-', color='b', label='Vitesse du vent')


    ax.legend()

    ax.set_xlabel('Temps (24h)')
    ax.set_ylabel('Vitesse du vent (km/h)')

    
    plt.xticks(rotation=45)

    ax.set_xticks(ax.get_xticks()[::4])
    plt.tight_layout()

    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)

    plt.close(fig)

    return send_file(img, mimetype='image/png')


@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", error_code=404), 404

@app.errorhandler(500)
def error(error):
    return render_template("error.html", error_code=500), 500

def init():
    return app