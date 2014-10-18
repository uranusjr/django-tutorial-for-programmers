from django.views.generic import CreateView, DetailView
from .models import Event
from .forms import EventForm


class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    http_method_names = ('post',)


class EventDetailView(DetailView):
    model = Event
