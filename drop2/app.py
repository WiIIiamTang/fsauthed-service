from flask import Flask, request
import requests
import json
import os
import sqlite3
import uuid
from datetime import datetime, timedelta

app = Flask(__name__)


@app.before_request
def middle_fleet_auth():
    print(request.endpoint, request.url, request.path)

    if request.headers.get("Authorization") is None:
        return "Invalid request", 400

    token = request.headers.get("Authorization").split(" ")[1]
    # get form data
    bodydata = request.form.to_dict()
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
    drop2_auth = bodydata.get("dname") in [
        d.get("name")
        for d in r.json().get("directives")
        if d.get("serviceId") == bodydata.get("serviceId")
    ]
    print("drop2 auth:", drop2_auth)
    if r.json().get("success") is None or not r.json().get("success") or not drop2_auth:
        return "Unauthorized", 401


@app.route("/drop2/bill/panel", methods=["POST"])
def upload():
    file_to_upload = request.files["file"]
    print("received file:", file_to_upload)
    if file_to_upload:
        file_id = str(uuid.uuid4())
        path = os.path.join(
            "..", "drop1", "files", f"{file_id}_{file_to_upload.filename}"
        )
        file_to_upload.save(path)
        con = sqlite3.connect(os.path.join("..", "drop1", "drop1.db"))
        cur = con.cursor()
        ident = str(uuid.uuid4())

        cur.execute(
            "INSERT INTO files (ident, ident_user_friendly, file_id, path, uses_left, uses_total, created_at, expires_at, file_size) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                ident,
                "bill",
                file_id,
                f"{file_id}_{file_to_upload.filename}",
                2,
                0,
                str(datetime.now()),
                str(datetime.now() + timedelta(hours=2)),
                int(request.content_length),
            ),
        )
        con.commit()
        con.close()
        return (
            f"File uploaded successfully: http://drop.williamtang.me/hooks/public/down/wlimit/{ident}/{file_id}",
            200,
        )
    return "File upload failed", 400
