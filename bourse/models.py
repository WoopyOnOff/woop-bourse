from datetime import datetime
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.forms import ModelForm
from django.template.defaultfilters import date as _date
from ckeditor.fields import RichTextField

# Create your models here.
class Event(models.Model):
    # Modele des evenements
    event_name = models.CharField(max_length=200)
    event_location = models.CharField(max_length=200)
    event_date = models.DateTimeField('Event Date')
    STATUSES = ((1,'Saisie Ouverte'),(2,'Saisie Fermée'),(3,'Bourse Ouverte'),(4,'Bourse Fermée'),)
    status = models.IntegerField('Event Status',default=2,choices=STATUSES)
    comments = RichTextField()
    def __str__(self):
        return self.event_name + ' - ' + _date(self.event_date,'d F Y')
    def get_absolute_url(self):
        return reverse('bourse:event-detail', kwargs={"pk": self.id})
    def date_only(self):
        return _date(self.event_date,'d F Y')
    def hour_only(self):
        return _date(self.event_date,'H:i')
    def status_desc(self):
        val = self.STATUSES[( self.status - 1 )][1]
        return val

class UserList(models.Model):
    # Modele des listes de jeux des utilisateurs
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    LIST_STATUSES = ((1,'Editable'),(2,'Validated'),(3,'Admin validated'),(4,'Archived'),)
    list_status = models.IntegerField('List Status',default=1,choices=LIST_STATUSES)
    created_date = models.DateTimeField('Date Created', auto_now_add=True)
    validated_date = models.DateTimeField('Date Validated',blank=True,null=True)
    def is_editable(self):
        if self.list_status == 1:
            return True
        else:
            return False
    def event_status(self):
        return self.event.status
    def event_status_desc(self):
        return self.event.status_desc()
    def list_label(self):
        return self.event.event_name + ' du ' + self.event.date_only()
    def status_desc(self):
        val = self.LIST_STATUSES[( self.list_status - 1 )][1]
        return val
    def item_set_sorted(self):
        return self.list_items.all().order_by('-created_date')
    def get_absolute_url(self):
        return reverse('bourse:my-list-view',kwargs={"pk": self.id})
    def __str__(self):
        return self.user.username + ' - ' + self.event.event_name + ' - ' + self.event.date_only() + ' - ' + self.status_desc()

class Item(models.Model):
    # Modele des jeux appartenant aux listes
    list = models.ForeignKey(UserList, on_delete=models.CASCADE, related_name='list_items')
    name = models.CharField(max_length=100)
    price = models.IntegerField('Sold Price')
    created_date = models.DateTimeField('Date Created', auto_now_add=True)
    is_sold = models.BooleanField('Item Sold',default=False)
    sold_date = models.DateTimeField('Date Sold',blank=True,null=True)
    copied_from = models.IntegerField('Copied from',blank=True,null=True,editable=False)
    copied_to = models.IntegerField('Copied to',blank=True,null=True,editable=False)
    def __str__(self):
        return str(self.pk) + ' - ' + self.name
    def code(self):
        item_code = str(self.pk) + ' - ' + self.name
        return item_code
    def delete(self):
        if self.copied_from is not None:
            source = Item.objects.get(pk=self.copied_from)
            source.copied_to = None
            source.save()
        if self.copied_to is not None:
            copy = Item.objects.get(pk=self.copied_to)
            copy.copied_from = None
            copy.save()
        super(Item,self).delete()

class Order(models.Model):
    # Modele des bons de vente
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    created_date = models.DateTimeField('Date Created', auto_now_add=True)
    is_validated = models.BooleanField('Order Validated',default=False)
    def __str__(self):
        return str(self.pk) + ' - ' + self.event.event_name + ' - ' + _date(self.created_date,'d/m/Y H:i:s')
    # Commande pas éditable si validée, ou pas validé mais que le status de la bourse est différent de 3 (ouverte)
    def is_editable(self):
        if self.is_validated: 
            return False
        elif not self.is_validated and self.event.status != 3:
            return False
        else:
            return True

class OrderItem(models.Model):
    # Modele des elements (jeux) des bons de vente
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='item')
    add_date = models.DateTimeField('Date Added', auto_now_add=True, null=True)
    def __str__(self):
        return str(self.order.id) + ' ' + self.item.name
    def itemprice(self):
        return self.item.price

class Page(models.Model):
    title = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50,null=True)
    content = RichTextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title