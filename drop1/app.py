from flask import Flask, request, send_file
import requests
import json
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
con = sqlite3.connect("drop1.db")
cur = con.cursor()
cur.execute(
    "CREATE TABLE IF NOT EXISTS files (ident TEXT, ident_user_friendly TEXT, file_id TEXT, path TEXT, uses_left INTEGER, uses_total INTEGER, created_at TEXT, expires_at TEXT, file_size TEXT)"  # noqa
)
cur.execute(
    "CREATE TABLE IF NOT EXISTS downloaded_by (ident TEXT, file_id TEXT, ip_address TEXT)"
)
con.commit()
con.close()


@app.route("/")
def hello_world():
    return "<h3>drop-1 compute</h3>"


@app.route("/hooks/public/down/wlimit/<string:ident>/<string:file_id>/d")
def hooks_public_down_wlimit(ident, file_id):
    connection = sqlite3.connect("drop1.db")
    cursor = connection.cursor()
    res = cursor.execute(
        "SELECT file_id, ident_user_friendly, path, uses_left, expires_at FROM files WHERE ident=? AND file_id=?",  # noqa
        (ident, file_id),
    )
    res = res.fetchall()
    if len(res) == 0:
        return "File not found", 404

    res = res[0]
    if res[3] <= 0:
        # delete the file
        try:
            os.remove(os.path.join(os.getcwd(), "files", res[2]))
        except FileNotFoundError:
            pass
        return "You cannot download this anymore", 400

    # also check if expired
    if datetime.now() > datetime.strptime(res[4].split(".")[0], "%Y-%m-%d %H:%M:%S"):
        # delete the file
        try:
            os.remove(os.path.join(os.getcwd(), "files", res[2]))
        except FileNotFoundError:
            pass
        return "This file has expired", 400

    # abs path
    file_path = os.path.abspath(os.path.join(os.getcwd(), "files", res[2]))
    fid = res[0]

    cursor.execute(
        f"UPDATE files SET uses_left=uses_left-1 WHERE ident=? AND file_id=?",  # noqa
        (ident, file_id),
    )
    cursor.execute(
        f"INSERT INTO downloaded_by (ident, file_id, ip_address) VALUES (?, ?, ?)",  # noqa
        (ident, file_id, request.access_route[-1]),
    )
    connection.commit()
    connection.close()

    return send_file(file_path, as_attachment=True, download_name=f"{res[2]}")


@app.route("/hooks/public/down/wlimit/<string:ident>/<string:file_id>")
def hooks_public_down_wlimit_page(ident, file_id):
    connection = sqlite3.connect("drop1.db")
    cursor = connection.cursor()
    res = cursor.execute(
        f"SELECT ident_user_friendly, path, file_id, uses_left, ident, created_at, expires_at, file_size FROM files WHERE ident=? AND file_id=?",  # noqa
        (ident, file_id),
    )
    res = res.fetchall()
    if len(res) == 0:
        return "File not found", 404

    res = res[0]
    if res[3] <= 0:
        # delete the file
        try:
            os.remove(os.path.join(os.getcwd(), "files", res[1]))
        except FileNotFoundError:
            pass
        return "You cannot download this anymore", 400

    # also check if expired
    if datetime.now() > datetime.strptime(res[6].split(".")[0], "%Y-%m-%d %H:%M:%S"):
        # delete the file
        try:
            os.remove(os.path.join(os.getcwd(), "files", res[1]))
        except FileNotFoundError:
            pass
        return "This file has expired", 400

    ident_user_friendly = res[0]
    fid = res[2]
    path = res[1]
    connection.close()

    return f"<h2>{ident_user_friendly} wants to send a file over: {path} created at {res[5]}, expires at {res[6]} </h2> <br /><a href='/hooks/public/down/wlimit/{res[4]}/{fid}/d'>Download</a> <br /> <p>Uses left: {res[3]}</p><p>Original request size: {res[7]}B</p>"  # noqa


@app.before_request
def middle_fleet_auth():
    print(request.endpoint, request.url, request.path)
    if (
        request.endpoint == "hello_world"
        or "hooks_public_down_onetime"
        or "hooks_public_down_onetime_page"
    ):
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
    drop1_auth = bodydata.get("dname") in [
        d.get("name")
        for d in r.json().get("directives")
        if d.get("serviceId") == bodydata.get("serviceId")
    ]
    print("auth:", drop1_auth)
    if r.json().get("success") is None or not r.json().get("success") or not drop1_auth:
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

    logname = f'logs/log_{datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}.txt'
    with open(logname, "w") as f:
        f.write(textdata)

    return "OK", 200
