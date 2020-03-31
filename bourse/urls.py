from django.urls import path

from . import views

#app_name = 'bourse'
urlpatterns = [
    # ex: /polls/
    path('', views.index, name='index'),
    path('events/',views.EventListView.as_view(),name='events'),
    path('event/<int:pk>',views.EventDetailView.as_view(), name='event-detail'),
    # ex: /polls/5/
    #path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    # ex : /polls/5/results/
    #path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    # ex: /polls/5/vote/
    #path('<int:question_id>/vote/', views.vote, name='vote'),
]