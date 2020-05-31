from django import forms
from django.forms.models import inlineformset_factory, BaseInlineFormSet, modelformset_factory
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User
from .models import Item, UserList, Event, Order, OrderItem

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name','last_name','email']

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
############################
# Adminitration
############################
class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('status',)

class OrderModelForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('is_validated',)

OrderItemFormset = modelformset_factory(OrderItem,fields=('item',),extra=1)

class ItemTextForm(forms.Form):
    item_pk = forms.IntegerField(label='Code du jeu',help_text=_('Entrer le code du jeu à ajouter.'))
    def __init__(self, *args, **kwargs):
        event_id = kwargs.pop('event_id', None)
        super(ItemTextForm, self).__init__(*args, **kwargs)
    def clean_item_pk(self):
        data = self.cleaned_data['item_pk']
        if not Item.objects.filter(pk=data,is_sold=False).exists() or OrderItem.objects.filter(item=data):
            raise ValidationError(_('Jeu non trouvé, ou déjà vendu.'), code='invalid')
        return data
# Orders
#OrderItemFormset = inlineformset_factory(Order, OrderItem, fields=('item',),extra=1,widgets={'item:':forms.TextInput(attrs={'class': 'form-control','placeholder':'Entrer le code du jeu'})})

class ListManageForm(forms.ModelForm):
    class Meta:
        model = UserList
        fields = ('list_status',)
