import socket
import json
import httpx as http

from urllib.parse import urlparse
from django.core.exceptions import BadRequest
from django.conf import settings

def _eval(expr):
    uri_data = urlparse(settings.PREPL_URI)
    if uri_data.scheme != "tcp":
        raise BadRequest(f"invalid PREPL_URI: {settings.PREPL_URI}")

    if not isinstance(uri_data.netloc, str):
        raise BadRequest(f"invalid PREPL_URI: {settings.PREPL_URI}")

    host, port = uri_data.netloc.split(":", 2)

    if port is None:
        port = 6063

    if isinstance(port, str):
        port = int(port)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.send(expr.encode("utf-8"))

        with s.makefile() as f:
            data = f.readline()
            result = json.loads(data)
            return result["val"]

def derive_password_hash(password):
    expr = "(app.srepl.ext/derive-password {})\n".format(
        json.dumps(password)
    )
    return _eval(expr)

def create_profile(fullname, email, password):
    expr = "(app.srepl.ext/create-profile {}, {}, {})".format(
        json.dumps(fullname),
        json.dumps(email),
        json.dumps(password)
    )
    return _eval(expr)

