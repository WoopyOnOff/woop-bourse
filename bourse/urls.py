from django.urls import path

from . import views

#app_name = 'bourse'
urlpatterns = [
    path('', views.index, name='index'),
    path('events/',views.EventListView.as_view(),name='events'),
    path('event/<int:pk>',views.EventDetailView.as_view(), name='event-detail'),
    path('event/<int:event_id>/<int:user_id>/participate',views.user_list_create_or_view,name='user-list-create-or-view'),
    path('mylists/',views.ListsByUserListView.as_view(),name='my-lists'),
    path('mylists/<int:pk>',views.ListsByUserListView.as_view(),name='my-lists'),
    path('mylist/<int:pk>/view',views.ListDetailByUserDetailView.as_view(),name='my-list-view'),
    path('mylist/<int:list_id>/item/<int:pk>/delete/',views.ItemDelete.as_view(),name='del-item-from-list'),
    path('mylist/<int:list_id>/item/<int:pk>/update/',views.ItemUpdate.as_view(),name='edit-item-from-list'),
    path('mylist/<int:list_id>/item/create',views.ItemCreate.as_view(),name='add-item-to-list'),
]