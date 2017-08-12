from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^signers/$', views.petition_signers, name='petition_signers'),
    url(r'^signers/search/json/$', views.SearchPetitionSignersJson.as_view(), name='petition_signers_search_json'),
]
