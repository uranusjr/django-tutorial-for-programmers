from django.conf.urls import patterns, include, url
from django.contrib import admin
from stores.views import home, store_list, store_detail


urlpatterns = patterns(
    '',
    url(r'^$', home, name='home'),
    url(r'^store/$', store_list, name='store_list'),
    url(r'^store/(?P<pk>\d+)/$', store_detail, name='store_detail'),
    url(r'^admin/', include(admin.site.urls)),
)
