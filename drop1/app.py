from flask import Flask, request
import requests
import json

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<h3>drop-1 compute</h3>"


@app.route("/heartbeat", methods=["POST"])
def heartbeat():
    token = request.headers.get("Authorization")
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
    print(r.json())
    print(
        "drop1 receiving heartbeat check:",
        bodydata.get("dname")
        in [
            d.get("name")
            for d in r.json().get("directives")
            if d.get("serviceId") == bodydata.get("serviceId")
        ],
    )
    if not r.json().get("success"):
        return "Unauthorized", 401

    return "OK", 200
