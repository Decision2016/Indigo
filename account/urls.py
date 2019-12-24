from django.conf.urls import url
from account import views

urlpatterns = [
    url(r'^register', views.UserRegAPI.as_view()),
    url(r'^login', views.UserLoginAPI.as_view()),
    url(r'^logout', views.UserLoginOutAPI.as_view()),
    url(r'^check_username', views.CheckUsernameExistAPI.as_view()),
    url(r'^profile', views.ProfileAPI.as_view()),
    url(r'^commands', views.CommandAPI.as_view()),
    url(r'^get_command_total', views.CommandTotalGetAPI.as_view()),
    url(r'^groups', views.GroupAPI.as_view()),
    url(r'^person', views.PersonAPI.as_view()),
]