from django.contrib import admin

# Register your models here.
from .models import Event, UserList, Order, Item, OrderItem, Page


# Event
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('event_name','event_date','status')
    list_filter = ('event_date','status')

# Item
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name','price','is_sold','sold_date','list')
    fields = [('name','price')]
    list_filter = ['is_sold','list__event']

class ItemInline(admin.TabularInline):
    model = Item

# UserList
@admin.register(UserList)
class UserListAdmin(admin.ModelAdmin):
    list_display = ('user','event','list_status','created_date','validated_date')
    inlines = [ItemInline]
    list_filter = ['list_status','event']

# Order
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    #fields = [('code')]

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id','event','created_date','is_validated')
    inlines = [OrderItemInline]
    list_filter = ['is_validated','event']

# Page
@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    read_only_fields = ['created', 'timestamp']