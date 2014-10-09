from django.conf.urls import patterns, url
from . import views


urlpatterns = patterns(
    '',
    url(r'^$', views.store_list, name='store_list'),
    url(r'^(?P<pk>\d+)/$', views.store_detail, name='store_detail'),
)
