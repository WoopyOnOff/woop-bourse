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
        return self.item_set.all().order_by('-created_date')
    def get_absolute_url(self):
        return reverse('bourse:my-list-view',kwargs={"pk": self.id})
    def __str__(self):
        return self.user.username + ' - ' + self.event.event_name + ' - ' + self.event.date_only() + ' - ' + self.status_desc()

class Item(models.Model):
    # Modele des jeux appartenant aux listes
    list = models.ForeignKey(UserList, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.IntegerField('Sold Price')
    created_date = models.DateTimeField('Date Created', auto_now_add=True)
    is_sold = models.BooleanField('Item Sold',default=False)
    sold_date = models.DateTimeField('Date Sold',blank=True,null=True)
    def __str__(self):
        return str(self.pk) + ' - ' + self.name
    def code(self):
        item_code = str(self.pk) + ' - ' + self.name
        return item_code

class Order(models.Model):
    # Modele des bons de vente
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    created_date = models.DateTimeField('Date Created', auto_now_add=True)
    is_validated = models.BooleanField('Order Validated',default=False)
    def __str__(self):
        return str(self.pk) + ' - ' + self.event.event_name + ' - ' + _date(self.created_date,'d/m/Y H:i:s')
    # def nb_items(self):
    #     items = self.annotate(items_count=models.Count('order_items'))
    #     return items.items_count

class OrderItem(models.Model):
    # Modele des elements (jeux) des bons de vente
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='item')
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