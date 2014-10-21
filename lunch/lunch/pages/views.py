from django.shortcuts import render
from events.models import Event


def home(request):
    try:
        current_event = Event.objects.latest()
    except Event.DoesNotExist:
        current_event = None
    return render(request, 'pages/home.html', {'current_event': current_event})
