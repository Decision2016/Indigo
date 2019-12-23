from django.conf.urls import url, include
from server.views import ServerAPI

urlpatterns = [
    url(r'^server/', ServerAPI.as_view())
]