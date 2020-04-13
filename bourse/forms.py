from django import forms
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from .models import Item, UserList

class ItemForm(forms.ModelForm):
    name = forms.CharField(label='Nom du jeu')
    price = forms.IntegerField(label='Prix de vente',help_text=_('(Commission de 1€ incluse)'))
    def clean_price(self):
        data = self.cleaned_data['price']
        if data < 1:
            raise ValidationError(_('Valeur non valide - Entrez un prix supérieur à 1€'), code='invalid')
        return data
    class Meta:
        model = Item
        fields = ['name','price']

#ItemFormSet = inlineformset_factory(UserList,Item,form=ItemForm,fields=('name','price',),extra=1,can_delete=True)

class ListValidateForm(forms.Form):
    description_text = _('Êtes-vous certain de vouloir valider votre formulaire ? Cette action est irréversible.')
    class Meta:
        model = UserList
        fields = None