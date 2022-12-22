import httpx as http

from django.core.exceptions import BadRequest
from django.contrib.auth import get_user_model
from django.conf import settings

def get_api_uri():
    api_uri = settings.API_URI

    if not api_uri.endswith("/"):
        api_uri = api_uri + "/"

    return api_uri

def resolve_uri(path):
    return f"{get_api_uri()}{path}"


DEFAULT_HEADERS = {
    "accept": "application/json",
    "content-type": "application/json"
}

import traceback

def authenticate(username, password):
    user_model = get_user_model()

    url = resolve_uri("api/rpc/command/login-with-password")
    data = {
        "email": username,
        "password": password,
        "scope": "admin"
    }

    response = http.post(url, json=data, headers=DEFAULT_HEADERS)
    if response.status_code == 200:
        token = response.cookies.get("auth-token")
        data = response.json()

        if data.get("isAdmin", False) and token:
            user = user_model._default_manager.get_by_natural_key(username)
            return user, token

    return None, None

def check_password(token, profile_id, password):
    params = {
        "profileId": str(profile_id),
        "password": password
    }

    cookies = {
        "auth-token": token
    }

    url = resolve_uri("api/rpc/command/check-profile-password")
    response = http.post(url, json=params, cookies=cookies, headers=DEFAULT_HEADERS)
    if response.status_code != 200:
        raise BadRequest("unable to check password")

    data = response.json();
    return data["valid"]


def get_password_hash(token, profile_id, password):
    params = {
        "profileId": str(profile_id),
        "password": password
    }

    cookies = {
        "auth-token": token
    }

    url = resolve_uri("api/rpc/command/get-derived-password")
    response = http.post(url, json=params, cookies=cookies, headers=DEFAULT_HEADERS)
    if response.status_code != 200:
        raise BadRequest("unable to get password hash")

    data = response.json();
    return data["password"]
