from django.shortcuts import get_object_or_404,render,redirect
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.utils import timezone
from django.template import loader
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils.translation import ugettext_lazy as _

# Create your views here.
from .models import Event, UserList, Item
from .forms import ItemForm

def index(request):
    opened_registration_event = Event.objects.filter(status=1)
    context = {
        'opened_registration_event': opened_registration_event,
    }
    return render(request, 'index.html', context=context)

class EventListView(generic.ListView):
    model = Event

class EventDetailView(generic.DetailView):
    model = Event

class ListsByUserListView(LoginRequiredMixin,generic.ListView):
    model = UserList
    template_name = 'bourse/lists_by_user.html'
    paginate_by = 5
    def get_queryset(self):
        return UserList.objects.filter(user=self.request.user).order_by('created_date')

class ListDetailByUserDetailView(LoginRequiredMixin,generic.DetailView):
    model = UserList
    template_name = 'bourse/list_detail_by_user.html'
    def get_queryset(self):
        return UserList.objects.filter(user=self.request.user).order_by('created_date')

class ItemCreate(LoginRequiredMixin,CreateView):
    model = Item
    form_class = ItemForm
    def get_queryset(self):
        return Item.objects.filter(list__user=self.request.user,list=self.kwargs.get('list_id'),list__event__status=1)
    def form_valid(self, form):
        form.instance.list__user = self.request.user
        self.object = form.save(commit=False)
        self.object.list_id = self.kwargs.get('list_id', None)
        if UserList.objects.filter(user=self.request.user,id=self.object.list_id,event__status=1):
            self.object.save()
            return redirect('my-list-view',self.object.list_id)
        else:
            return HttpResponseForbidden()

class ItemUpdate(LoginRequiredMixin,UpdateView):
    model = Item
    form_class = ItemForm
    def get_queryset(self):
        return Item.objects.filter(list__user=self.request.user,id=self.kwargs.get('pk'),list__event__status=1)
    def form_valid(self, form):
        form.instance.list__user = self.request.user
        self.object = form.save(commit=False)
        self.object.list_id = self.kwargs.get('list_id', None)
        if UserList.objects.filter(user=self.request.user,id=self.object.list_id,event__status=1):
            self.object.save()
            return redirect('my-list-view',self.object.list_id)
        else:
            return HttpResponseForbidden()

class ItemDelete(LoginRequiredMixin,DeleteView):
    model = Item
    def get_queryset(self):
        return Item.objects.filter(list__user=self.request.user,id=self.kwargs.get('pk'))
    def get_success_url(self):
        return reverse_lazy('my-list-view',kwargs={'pk':self.kwargs.get('list_id','')})

@login_required
def user_list_create_or_view(request, event_id, user_id):
    event_inst = get_object_or_404(Event,id=event_id)
    user_list, created = UserList.objects.get_or_create(event=event_inst,user=request.user)
    return redirect('my-lists')
