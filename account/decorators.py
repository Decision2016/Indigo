from rest_framework.response import Response
from .models import User
import functools


class BaseDecorator(object):
    def __init__(self, func):
        self.func = func

    def __get__(self, obj, obj_type):
        return functools.partial(self.__call__, obj)

    @staticmethod
    def error(msg):
        return Response({"errMsg": "Permission Denied", "data": msg})

    def __call__(self, *args, **kwargs):
        self.request = args[1]

        if self.check_permission():
            return self.func(*args, **kwargs)
        else:
            return self.error("Please Login")

    def check_permission(self):
        raise NotImplementedError()


class login_required(BaseDecorator):
    def check_permission(self):
        user = self.request.user
        return user.is_authenticated


class api_permission_required(BaseDecorator):
    def check_permission(self):
        data = self.request.data
        username = data['username']
        app_secret = data['app_secret']
        user = User.objects.get(username=username)
        if(user.openSecret == _):
            return True
        else:
            return False


class cq_permission_required(BaseDecorator):
    def check_permission(self):
        username = self.request.query_params['username']
        open_secret = self.request.query_params['app_secret']
        user = User.objects.get(username=username)
        if user.openSecret == open_secret:
            return True
        else:
            return False
