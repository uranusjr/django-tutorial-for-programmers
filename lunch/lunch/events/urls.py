from django.conf.urls import patterns, url
from . import views


urlpatterns = patterns(
    '',
    url(r'^new/$', views.EventCreateView.as_view(), name='event_create'),
    url(r'^(?P<pk>\d+)/$', views.EventDetailView.as_view(),
        name='event_detail'),
)
