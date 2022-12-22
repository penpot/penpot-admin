import httpx as http

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.core.cache import cache

from penpot_admin import core
from penpot_admin import api

class PenpotBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)

        if username is None or password is None:
            return

        user, token = api.authenticate(username, password)

        if user and token:
            session = core.get_current_session()
            if session:
                session["auth-token"] = token
            return user

        return None

    def get_user(self, user_id):
        user_model = get_user_model()
        try:
            user = user_model._default_manager.get(pk=user_id)
        except user_model.DoesNotExist:
            return None
        return user if self.can_authenticate(user) else None

    def get_user_permissions(self, user_obj, obj=None):
        return set()

    def get_group_permissions(self, user_obj, obj=None):
        return set()

    def get_all_permissions(self, user_obj, obj=None):
        return {
            *self.get_user_permissions(user_obj, obj=obj),
            *self.get_group_permissions(user_obj, obj=obj),
        }

    def has_perm(self, user_obj, perm, obj=None):
        return perm in self.get_all_permissions(user_obj, obj=obj)

    def can_authenticate(self, user):
        is_active = getattr(user, 'is_active', None)
        return is_active or is_active is None
