import requests
import argparse
import json
from subprocess import Popen, PIPE


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--key", "-k", help="path to key file")
    parser.add_argument(
        "--root", "-r", help="abs path to root directory of this git repo"
    )
    args = parser.parse_args()

    keydata = {}
    with open(args.key) as f:
        keydata = json.load(f)

    ENDPOINT = "https://fleet.williamtang.me/api"
    status = {"connected": False, "authorized": False}

    r = requests.post(
        f"{ENDPOINT}/fleet/service/connectuser",
        json={
            "discordAccountId": keydata.get("shared_id"),
            "discordUsername": keydata.get("shared_idname"),
            "serviceId": keydata.get("serviceId"),
            "serviceNameIdentifier": keydata.get("serviceNameIdentifier"),
        },
        headers={
            "Content-Type": "application/json",
            "Authorization": f'Bearer {keydata.get("AUTH_KEY")}',
        },
    )
    status["connected"] = r.json().get("success")

    r = requests.get(
        f"{ENDPOINT}/fleet/service/directive?discordAccountId={keydata.get('shared_id')}",
        headers={
            "Content-Type": "application/json",
            "Authorization": f'Bearer {keydata.get("AUTH_KEY")}',
        },
    )
    status["authorized"] = keydata.get("dname") in [
        d.get("name")
        for d in r.json().get("directives")
        if d.get("serviceId") == keydata.get("serviceId")
    ]
    print(status)

    if not status.get("connected") or not status.get("authorized"):
        return

    r = requests.get(
        f"{ENDPOINT}/fleet/stats?serviceId={keydata.get('serviceId')}&serviceNameIdentifier={keydata.get('serviceNameIdentifier')}&discordAccountId={keydata.get('shared_id')}&statCategory=_fs_ping&statDescription=_fs_ping&statName=_fs_ping_connect",
        headers={
            "Content-Type": "application/json",
            "Authorization": f'Bearer {keydata.get("AUTH_KEY")}',
        },
    )
    fsp_value = r.json().get("stats")[0].get("statValue")

    r = requests.patch(
        f"{ENDPOINT}/fleet/stats",
        json={
            "serviceId": keydata.get("serviceId"),
            "serviceNameIdentifier": keydata.get("serviceNameIdentifier"),
            "discordAccountId": keydata.get("shared_id"),
            "statCategory": "_fs_ping",
            "statDescription": "_fs_ping",
            "statValue": str(int(fsp_value) + 1),
            "statName": "_fs_ping_connect",
        },
        headers={
            "Content-Type": "application/json",
            "Authorization": f'Bearer {keydata.get("AUTH_KEY")}',
        },
    )
    if not r.json().get("success"):
        raise RuntimeError("Failed to run patch request")

    p = Popen(
        [
            "git",
            "pull",
        ],
        cwd=args.root,
        stdout=PIPE,
        stderr=PIPE,
    )
    out, err = p.communicate()
    print(str(out))
    print(str(err))

    r = requests.post(
        f"{keydata.get('drop1')}/heartbeat",
        json={
            "dname": keydata.get("dname"),
            "serviceId": keydata.get("serviceId"),
            "shared_id": keydata.get("shared_id"),
        },
        headers={
            "Content-Type": "application/json",
            "Authorization": f'Bearer {keydata.get("AUTH_KEY")}',
        },
    )
    print("HEARTBEAT", r.text)

    p = Popen(
        [
            "df",
            "-h",
            "/",
        ],
        cwd=args.root,
        stdout=PIPE,
        stderr=PIPE,
    )
    out, err = p.communicate()

    r = requests.post(
        f"{keydata.get('drop1')}/hooks/save/log",
        json={
            "dname": keydata.get("dname"),
            "serviceId": keydata.get("serviceId"),
            "shared_id": keydata.get("shared_id"),
            "textdata": out.decode("utf-8"),
        },
        headers={
            "Content-Type": "application/json",
            "Authorization": f'Bearer {keydata.get("AUTH_KEY")}',
        },
    )
    print("LOG", r.text)


if __name__ == "__main__":
    main()
