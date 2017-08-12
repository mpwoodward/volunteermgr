from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.list, name='list'),
    url(r'^events/json/$', views.EventsJson.as_view(), name='events_json'),
    url(r'^(\d+)/$', views.event_detail, name='event_detail'),
    url(r'^(\d+)/tab/detail/$', views.event_detail_tab, name='event_detail_tab'),
    url(r'^(\d+)/tab/attendees/$', views.event_attendees_tab, name='event_attendees_tab'),
    url(r'^add/$', views.edit_event, name='add_event'),
    url(r'^(\d+)/edit/$', views.edit_event, name='edit_event'),
]
