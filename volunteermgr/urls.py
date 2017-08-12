"""volunteermgr URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from ajax_select import urls as ajax_select_urls

from django.conf.urls import url, include
from django.contrib import admin
from django.core.urlresolvers import reverse_lazy
from django.views.generic.base import RedirectView


urlpatterns = [
    url(r'^ajax_select/', include(ajax_select_urls)),
    url(r'^admin/', admin.site.urls),
    url(r'^$', RedirectView.as_view(url=reverse_lazy('volunteer:search'))),
    url(r'^contact/', include('contact.urls', namespace='contact')),
    url(r'^organization/', include('organization.urls', namespace='organization')),
    url(r'^petition/', include('petition.urls', namespace='petition')),
    url(r'^phonecall/', include('phonecall.urls', namespace='phonecall')),
    url(r'^security/', include('security.urls', namespace='security')),
    url(r'^volunteer/', include('volunteer.urls', namespace='volunteer')),
]

admin.site.site_header = "Volunteer Manager"
