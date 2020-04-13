from django.contrib import admin

# Register your models here.
from .models import Event, UserList, Order, Item, OrderItem

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('event_name','event_date','status')
    list_filter = ('event_date','status')

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name','price','is_sold','sold_date')
    fields = [('name','price')]

class ItemInline(admin.TabularInline):
    model = Item

@admin.register(UserList)
class UserListAdmin(admin.ModelAdmin):
    inlines = [ItemInline]

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    #fields = [('code')]

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id','event','created_date','is_validated')
    inlines = [OrderItemInline]