from django.shortcuts import get_object_or_404,render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.template import loader
from django.contrib.auth import authenticate, login

# Create your views here.
from .models import Event

def index(request):
    opened_registration_event = Event.objects.filter(status=1)
    context = {
        'opened_registration_event': opened_registration_event,
    }
    # output = ', '.join([e.event_name + " du "+ e.event_date.strftime("%d/%m/%Y") for e in opened_registration_event])
    return render(request, 'index.html', context=context)

class EventListView(generic.ListView):
    model = Event

class EventDetailView(generic.DetailView):
    model = Event