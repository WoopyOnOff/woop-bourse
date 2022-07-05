from django import forms
from django_registration.forms import RegistrationFormUniqueEmail
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

class CustomRegistrationForm(RegistrationFormUniqueEmail):
    first_name = forms.CharField(max_length=50,label=_('Prénom')) # Required
    last_name = forms.CharField(max_length=50,label=_('Nom')) # Required
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email','password1','password2']
      