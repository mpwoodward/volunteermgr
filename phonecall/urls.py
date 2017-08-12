from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^calls/$', views.calls, name='calls'),
    url(r'^calls/search/json/$', views.SearchCallsJson.as_view(), name='search_calls_json'),
]
