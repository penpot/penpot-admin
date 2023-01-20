import json
import socket
import uuid

from urllib.parse import urlparse
from django.core.exceptions import BadRequest
from django.conf import settings


def get_prepl_conninfo():
    uri_data = urlparse(settings.PREPL_URI)
    if uri_data.scheme != "tcp":
        raise RuntimeException(f"invalid PREPL_URI: {PREPL_URI}")

    if not isinstance(uri_data.netloc, str):
        raise RuntimeException(f"invalid PREPL_URI: {PREPL_URI}")

    host, port = uri_data.netloc.split(":", 2)

    if port is None:
        port = 6063

    if isinstance(port, str):
        port = int(port)

    return host, port

def send_eval(expr):
    host, port = get_prepl_conninfo()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.send(expr.encode("utf-8"))
        s.send(b":repl/quit\n\n")

        with s.makefile() as f:
            result = json.load(f)
            tag = result.get("tag", None)
            val = result.get("val", None)
            err = result.get("exception", None)

            if tag != "ret":
                raise RuntimeException("unexpected response from PREPL")

            if err:
                return None, val.get("via")[0]
            else:
                return val, None

def encode(val):
    return json.dumps(json.dumps(val))

def run_cmd(params):
    expr = "(app.srepl.ext/run-json-cmd {})".format(encode(params))
    val, err = send_eval(expr)
    if err:
        raise BadRequest(err["message"])
    return val

def derive_password_hash(password):
    params = {
        "cmd": "derive-password",
        "params": {
            "password": password,
        }
    }

    return run_cmd(params)

def create_profile(fullname, email, password):
    params = {
        "cmd": "create-profile",
        "params": {
            "fullname": fullname,
            "email": email,
            "password": password
        }
    }

    profile = run_cmd(params)
    return uuid.UUID(profile["id"])
