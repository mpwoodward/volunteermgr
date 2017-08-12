from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.search, name='search'),
    url(r'^search/json/$', views.SearchJson.as_view(), name='search_json'),
    url(r'^(\d+)/$', views.detail, name='detail'),
    url(r'^(\d+)/tab/detail/$', views.detail_tab, name='detail_tab'),
    url(r'^(\d+)/tab/notes', views.notes_tab, name='notes_tab'),
    url(r'^add/$', views.edit, name='add'),
    url(r'^edit/(\d+)/$', views.edit, name='edit'),
    url(r'^(\d+)/note/add/$', views.note_edit, name='note_add'),
    url(r'^(\d+)/note/edit/(\d+)/$', views.note_edit, name='note_edit'),
    url(r'^(\d+)/modal/detail/$', views.detail_modal, name='detail_modal'),
]