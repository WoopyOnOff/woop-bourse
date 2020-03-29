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
    template = loader.get_template('bourse/index.html')
    context = {
        'opened_registration_event': opened_registration_event,
    }
    # output = ', '.join([e.event_name + " du "+ e.event_date.strftime("%d/%m/%Y") for e in opened_registration_event])
    return HttpResponse(template.render(context, request))

class IndexView(generic.View):
    template_name = 'bourse/index.html'
    context_object_name = 'opened_registration_event'

    def get_queryset(self):
        """
        Return the Opened to registration event
        """
        return Event.objects.filter(
            status=1
        )
