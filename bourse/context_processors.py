from django.conf import settings

def site_params(request):
    return {'SITE_TITLE_SETTING': settings.SITE_TITLE, 'SITE_SIGNATURE_SETTING': settings.SITE_SIGNATURE}