from flask import Flask, request
import requests
import json

app = Flask(__name__)


@app.before_request
def middle_fleet_auth():
    print(request.endpoint, request.url, request.path)

    if request.headers.get("Authorization") is None:
        return "Invalid request", 400

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
        f"{ENDPOINT}/fleet/service/directive?discordAccountId={bodydata.get('shared_id')}",  # noqa
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
    )
    drop2_auth = (
        bodydata.get("dname")
        in [
            d.get("name")
            for d in r.json().get("directives")
            if d.get("serviceId") == bodydata.get("serviceId")
        ],
    )
    print("drop2 auth:", drop2_auth)
    if r.json().get("success") is None or not r.json().get("success") or not drop2_auth:
        return "Unauthorized", 401


@app.route("/", methods=["POST"])
def upload():
    file_to_upload = request.files["file"]
    if file_to_upload:
        file_to_upload.save("file.txt")
        return "File uploaded successfully", 200
