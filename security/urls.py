from django.conf.urls import url

from . import views


urlpatterns = [
    url('login/$', views.user_login, name='login'),
    url('logout/$', views.user_logout, name='logout'),
    url('password/change/$', views.change_password, name='change_password'),
    url('password/reset/$', views.reset_password, name='reset_password'),
]
