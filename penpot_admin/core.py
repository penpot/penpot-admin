from threading import local
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.core.cache import cache

_local_data = local()

class PenpotMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        _local_data.request = request
        _local_data.user = request.user

        return self.get_response(request)

def get_current_session():
    request = getattr(_local_data, "request")
    if request:
        return request.session
    return None
