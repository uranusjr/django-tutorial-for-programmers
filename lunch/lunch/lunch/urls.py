from django.conf.urls import patterns, include, url
from django.contrib import admin
from pages.views import home
from .api import v1, v2


urlpatterns = patterns(
    '',
    url(r'^$', home, name='home'),
    url(r'^event/', include('events.urls')),
    url(r'^store/', include('stores.urls')),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^api/v1/', include(v1.urls)),
    url(r'^api/', include(v2.urls)),
)
