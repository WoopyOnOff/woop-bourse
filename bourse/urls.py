from django.urls import path

from . import views

#app_name = 'bourse'
urlpatterns = [
    ### Index
    path('', views.index, name='index'),

    ### Événements
    # Liste des événements
    path('events/',views.EventListView.as_view(),name='events'),
    # Accès au détails d'un événement
    path('event/<int:pk>',views.EventDetailView.as_view(), name='event-detail'),
    # Participer à un événement (création d'une liste)
    path('event/<int:event_id>/participate',views.user_list_create_or_view,name='user-list-create-or-view'),
    
    ### Profil Utilisateur
    # Édition du profil de l'utilisateur
    path('profile/<int:pk>',views.ProfileUpdate.as_view(),name='profile-edit'),

    ### Listes Utilisateur
    # Listes crées par un utilisateur
    path('mylists/',views.ListsByUserListView.as_view(),name='my-lists'),
    # Détail d'une liste
    path('mylist/<int:pk>/view',views.ListDetailByUserDetailView.as_view(),name='my-list-view'),
    # Validation d'une liste par l'utilisateur
    path('mylist/<int:pk>/validate',views.ListValidate,name='validate-list'),
    # Ajout d'un élément à la liste
    path('mylist/<int:list_id>/item/create',views.ItemCreate.as_view(),name='add-item-to-list'),
    # Suppression d'un élément de la liste
    path('mylist/<int:list_id>/item/<int:pk>/delete/',views.ItemDelete.as_view(),name='del-item-from-list'),
    # Mise à jour d'un élément de la liste
    path('mylist/<int:list_id>/item/<int:pk>/update/',views.ItemUpdate.as_view(),name='edit-item-from-list'),

    ### Administration
    # Dashboard de l'événement
    path('admin/<int:event_id>/dashboard',views.Dashboard,name='admin-dashboard'),
    # Changer le status d'un événement
    path('admin/<int:pk>/edit',views.EventUpdate.as_view(),name='admin-event-update'),
    # Listes des utilisateurs
    path('admin/<int:pk>/managelists',views.ListsListView.as_view(),name='admin-lists-manage'),
    # Generation PDF depot et etiquettes / PDF Fin de vente
    path('admin/<int:event_id>/list/<int:list_id>/pdfgen/<str:var>',views.ListDetailPdfGen,name='admin-list-pdf'),
    # Changement de status d'une liste d'un utilisateur (détail)
    path('admin/<int:event_id>/list/<int:list_id>/validate',views.ListDetailValidate,name='admin-list-validate'),
    # Liste des bons de ventes
    path('admin/<int:event_id>/orders',views.OrdersListView.as_view(),name='admin-orders'),
    # Création d'un bon de vente
    path('admin/<int:event_id>/ordercreate',views.order_create,name='admin-ordercreate'),
    # Gestion du bon de vente (ajout d'éléments et validation)
    path('admin/<int:event_id>/order/<int:order_id>/manageorder',views.OrderDetailValidate,name='admin-ordermanage'),
    # Supression d'un élément du bon de vente
    path('admin/<int:event_id>/order/<int:order_id>/item/<int:pk>/delete',views.OrderItemDelete.as_view(),name='admin-order-item-delete'),
]