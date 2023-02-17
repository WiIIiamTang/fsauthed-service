from flask import Flask, request
import requests
import json
from datetime import datetime

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<h3>drop-1 compute</h3>"


@app.before_request
def middle_fleet_auth():
    print(request.endpoint, request.url, request.path)
    if request.endpoint == "hello_world":
        return

    token = request.headers.get("Authorization").split(" ")[1]
    bodydata = request.get_json()
    if type(bodydata) is not dict:
        try:
            bodydata = json.loads(bodydata)
        except Exception as e:
            print(e)
            return "Invalid body data", 400

    if not token or not bodydata:
        return "Invalid request", 400

    ENDPOINT = "https://fleet.williamtang.me/api"

    r = requests.get(
        f"{ENDPOINT}/fleet/service/directive?discordAccountId={bodydata.get('shared_id')}",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
    )
    print(
        "auth:",
        bodydata.get("dname")
        in [
            d.get("name")
            for d in r.json().get("directives")
            if d.get("serviceId") == bodydata.get("serviceId")
        ],
    )
    if r.json().get("success") is None or not r.json().get("success"):
        return "Unauthorized", 401


@app.route("/heartbeat", methods=["POST"])
def heartbeat():
    return "OK", 200


@app.route("/hooks/save/log", methods=["POST"])
def hooks_save_log():
    bodydata = request.get_json()
    if type(bodydata) is not dict:
        try:
            bodydata = json.loads(bodydata)
        except Exception as e:
            print(e)
            return "Invalid body data", 400

    textdata = bodydata.get("textdata")
    if not textdata:
        return "Invalid body data", 400

    logname = f'logs/log_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.txt'
    with open(logname, "w") as f:
        f.write(textdata)

    return "OK", 200
