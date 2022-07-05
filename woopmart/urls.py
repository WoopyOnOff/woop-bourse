"""woopmart URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.views.generic import RedirectView
from django.urls import include,path
from django_registration.forms import RegistrationFormUniqueEmail
from django_registration.backends.activation.views import RegistrationView
from .forms import CustomRegistrationForm

urlpatterns = [
    path('',RedirectView.as_view(url='bourse/',permanent=True)), # Redirection vers bourse/
    path('admin/', admin.site.urls),
    path('bourse/', include('bourse.urls')),
    path('accounts/register/',RegistrationView.as_view(form_class=CustomRegistrationForm),name='django_registration_register'),
    path('accounts/', include('django_registration.backends.activation.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]

