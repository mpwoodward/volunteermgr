from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.list, name='list'),
    url(r'^json/$', views.OrganizationsJson.as_view(), name='list_json'),
    url(r'^(\d+)/$', views.detail, name='detail'),
    url(r'^add/$', views.organization_form, name='add'),
    url(r'^(\d+)/edit/$', views.organization_form, name='edit'),
    url(r'^staff/$', views.staff, name='staff'),
    url(r'^staff/json/$', views.StaffJson.as_view(), name='staff_json'),
    url(r'^staff/add/$', views.staff_form, name='add_staff'),
    url(r'^staff/(?P<staff_id>\d+)/edit/$', views.staff_form, name='edit_staff'),
]
