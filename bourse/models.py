from datetime import datetime
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Event(models.Model):
    event_name = models.CharField(max_length=200)
    event_location = models.CharField(max_length=200)
    event_date = models.DateTimeField('Event Date')
    STATUSES = (
        (1,'Saisie Ouverte'),
        (2,'Saisie Fermée'),
        (3,'Bourse Ouverte'),
        (4,'Bourse Fermée'),
    )
    status = models.IntegerField('Event Status',default=2,choices=STATUSES)
    comments = models.TextField(max_length=2000)
    def __str__(self):
        return self.event_name
    def status_desc(self):
        if self.status==1:
            return 'Saisie Ouverte'
        elif self.status==2:
            return 'Saisie Fermée'
        elif self.status==3:
            return 'Bourse Ouverte'
        elif self.status==4:
            return 'Bourse Fermée'

class UserList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    LIST_STATUSES = (
        (1,'Editable'),
        (2,'Validated'),
        (3,'Archived'),
    )
    list_status = models.IntegerField('List Status',default=1,choices=LIST_STATUSES)
    created_date = models.DateTimeField('Date Created', auto_now_add=True)
    validated_date = models.DateTimeField('Date Validated',blank=True,null=True)
    def __str__(self):
        return self.user.username + ' - ' + self.event.event_name + ' - ' + self.event.event_date.strftime('%d/%m/%y') + ' - ' + str(self.list_status)
    def status_desc(self):
        if self.status==1:
            return 'Editable'
        elif self.status==2:
            return 'Validated'
        elif self.status==3:
            return 'Archived'

class Item(models.Model):
    list = models.ForeignKey(UserList, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.IntegerField('Sold Price')
    created_date = models.DateTimeField('Date Created', auto_now_add=True)
    is_sold = models.BooleanField('Item Sold',default=False)
    sold_date = models.DateTimeField('Date Sold',blank=True,null=True)
    def __str__(self):
        return self.name

class Order(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    created_date = models.DateTimeField('Date Created', auto_now_add=True)
    is_validated = models.BooleanField('Order Validated',default=False)
    def __str__(self):
        return self.event.event_name + ' ' + self.created_date.strftime('%d/%m/%y %H:%M:%S')

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.order.id) + ' ' + self.item.name