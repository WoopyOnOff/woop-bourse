from django.conf import settings
from .models import Event

def site_params(request):
    return {'SITE_TITLE_SETTING': settings.SITE_TITLE, 'SITE_SIGNATURE_SETTING': settings.SITE_SIGNATURE}

def active_event(request):
    active_event = Event.objects.filter(status__in=[1,2,3])
    return {'active_event':active_event}