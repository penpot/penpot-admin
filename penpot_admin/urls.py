import re

from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.urls import re_path
from django.views.static import serve
from penpot_admin.penpot.admin import admin_site

def static(prefix, view=serve, **kwargs):
    if not prefix:
        raise ImproperlyConfigured("Empty static prefix not permitted")

    return re_path(
        r"^%s(?P<path>.*)$" % re.escape(prefix.lstrip("/")), view, kwargs=kwargs
    )

urlpatterns = [
    static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
    path('admin/', admin_site.urls),
]
