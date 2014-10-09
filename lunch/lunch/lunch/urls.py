from django.conf.urls import patterns, include, url
from django.contrib import admin
from pages.views import home


urlpatterns = patterns(
    '',
    url(r'^$', home, name='home'),
    url(r'^store/', include('stores.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
