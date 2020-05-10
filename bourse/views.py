from django.shortcuts import get_object_or_404,render,redirect
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
import datetime

# Create your views here.
from .models import Event, UserList, Item, Order, OrderItem
from django.contrib.auth.models import User
from .forms import ItemForm, ListValidateForm, OrderModelForm, OrderItemFormset, ListManageForm

### Index ###
def index(request):
    opened_registration_event = Event.objects.filter(status=1)
    context = {
        'opened_registration_event': opened_registration_event,
    }
    return render(request, 'index.html', context=context)

### Profil Utilisateur ###
class ProfileUpdate(LoginRequiredMixin,UpdateView):
    model = User
    fields = ['first_name','last_name','email']
    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.id)
    def get_success_url(self):
        return reverse_lazy('profile-edit', kwargs={'pk':self.object.pk})

### Vues Événements ###

class EventListView(generic.ListView):
    model = Event

class EventDetailView(generic.DetailView):
    model = Event

### Vues sur les listes ###

# Création d'une liste si elle n'existe pas pour l'utilisateur
@login_required
def user_list_create_or_view(request, event_id, user_id):
    event_inst = get_object_or_404(Event,id=event_id,status=1)
    user_list, created = UserList.objects.get_or_create(event=event_inst,user=request.user)
    return redirect('my-lists')

# Listes de l'utilisateur
class ListsByUserListView(LoginRequiredMixin,generic.ListView):
    model = UserList
    template_name = 'bourse/lists_by_user.html'
    paginate_by = 5
    def get_queryset(self):
        return UserList.objects.filter(user=self.request.user).order_by('created_date')

# Detail liste de l'utilisateur
class ListDetailByUserDetailView(LoginRequiredMixin,generic.DetailView):
    model = UserList
    template_name = 'bourse/list_detail_by_user.html'
    def get_queryset(self):
        return UserList.objects.filter(user=self.request.user).order_by('created_date')

# Validation de la liste par l'utilisateur
@login_required
def ListValidate(request,pk):
    list_instance = get_object_or_404(UserList,pk=pk,user=request.user)
    success_url = redirect('my-list-view',list_instance.pk)
    if request.method == 'POST':
        if "cancel" in request.POST:
            return success_url
        else:
            form = ListValidateForm(request.POST)
            if form.is_valid():
                list_instance.list_status = 2
                list_instance.validated_date = datetime.datetime.now()
                list_instance.save()
                return success_url
    else:
        form = ListValidateForm()
    context = { 'form': form, 'list_instance': list_instance,}
    return render(request,'bourse/userlist_validate.html',context)

### Vues sur les éléments de liste ###

# Ajout d'un jeu à la liste de l'utilisateur
class ItemCreate(LoginRequiredMixin,CreateView):
    model = Item
    form_class = ItemForm
    def get_queryset(self):
        return Item.objects.filter(list__user=self.request.user,list__list_status=1,list=self.kwargs.get('list_id'),list__event__status=1)
    def form_valid(self, form):
        form.instance.list__user = self.request.user
        self.object = form.save(commit=False)
        self.object.list_id = self.kwargs.get('list_id', None)
        if UserList.objects.filter(user=self.request.user,id=self.object.list_id,event__status=1):
            self.object.save()
            return redirect('my-list-view',self.object.list_id)
        else:
            return HttpResponseForbidden()

# Mise à jour d'un jeu à la liste de l'utilisateur
class ItemUpdate(LoginRequiredMixin,UpdateView):
    model = Item
    form_class = ItemForm
    def get_queryset(self):
        return Item.objects.filter(list__user=self.request.user,list__list_status=1,id=self.kwargs.get('pk'),list__event__status=1)
    def form_valid(self, form):
        form.instance.list__user = self.request.user
        self.object = form.save(commit=False)
        self.object.list_id = self.kwargs.get('list_id', None)
        if UserList.objects.filter(user=self.request.user,id=self.object.list_id,event__status=1):
            self.object.save()
            return redirect('my-list-view',self.object.list_id)
        else:
            return HttpResponseForbidden()

# Suppression d'un jeu à la liste de l'utilisateur
class ItemDelete(LoginRequiredMixin,DeleteView):
    model = Item
    def get_queryset(self):
        return Item.objects.filter(list__user=self.request.user,list__list_status=1,id=self.kwargs.get('pk'),list__event__status=1)
    def get_success_url(self):
        return reverse_lazy('my-list-view',kwargs={'pk':self.kwargs.get('list_id','')})
    def post(self, request, *args, **kwargs):
        if "cancel" in request.POST:
            url = self.get_success_url()
            return HttpResponseRedirect(url)
        else:
            return super(ItemDelete, self).post(request, *args, **kwargs)

### Administration ###

# Dashboard pour la bourse
@login_required
def Dashboard(request,event_id):
    if request.user.is_staff == 1:
        event_inst = Event.objects.filter(id=event_id)
        user_lists_total = UserList.objects.filter(event=event_id).count()
        user_lists_validated = UserList.objects.filter(event=event_id,list_status=2).count()
        user_lists_editable = UserList.objects.filter(event=event_id,list_status=1).count()
        user_lists_adminvalidated = UserList.objects.filter(event=event_id,list_status=3).count()
        item_total = Item.objects.filter(list__event=event_id).count()
        item_sold_total = Item.objects.filter(list__event=event_id,is_sold=True).count()
        order_total = Order.objects.filter(event=event_id).count()
        order_unvalidated = Order.objects.filter(event=event_id,is_validated=False).count()
        context = {
            'event_inst':event_inst, 
            'user_lists_total':user_lists_total, 
            'user_lists_validated':user_lists_validated, 
            'user_lists_editable':user_lists_editable, 
            'user_lists_adminvalidated':user_lists_adminvalidated,
            'item_total':item_total,
            'item_sold_total':item_sold_total,
            'order_total':order_total,
            'order_unvalidated':order_unvalidated
        }
        return render(request, 'bourse/admin_dashboard.html', context=context)
    else:
        return HttpResponseForbidden()

# Visualisation des listes des utilisateurs
@login_required
def Managelists(request,event_id):
    if request.user.is_staff == 1:
        user_lists = UserList.objects.filter(event=event_id)
        context = {
            'user_lists':user_lists,
            'event_id':event_id,
        }
        return render(request,'bourse/admin_manage_lists.html',context=context)
    else:
        return HttpResponseForbidden()

# Visu et changement de status d'une liste
@login_required
def ListDetailValidate(request,event_id,list_id):
    template_name = 'bourse/admin_list_validate.html'
    user_list = get_object_or_404(UserList,pk=list_id,event=event_id)
    user_list_items = Item.objects.filter(list=list_id)
    success_url = redirect('admin-lists-manage',event_id)
    if request.user.is_staff == 1:
        if request.method == 'POST':
            if "cancel" in request.POST:
                return success_url
            else:
                form = ListManageForm(request.POST)
                if form.is_valid():
                    if form.cleaned_data['list_status'] == 1:
                        user_list.validated_date = None
                    user_list.list_status = form.cleaned_data['list_status']
                    user_list.save()
                    return success_url
        else:
            form = ListManageForm(initial={'list_status':user_list.list_status})
            context = { 
                'form':form,
                'user_list':user_list,
                'user_list_items':user_list_items}
            return render(request,template_name,context)
    else:
        return HttpResponseForbidden()

# WIP
class OrderCreate(PermissionRequiredMixin,CreateView):
    permission_required = 'order.can_add'
    model = Order
    fields = ['is_validated']
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["orderitem"] = OrderItemFormset(self.request.POST)
        else:
            data["orderitem"] = OrderItemFormset()
        return data
    def form_valid(self, form):
        context = self.get_context_data()
        orderitem = context["orderitem"]
        self.object = form.save()
        if orderitem.is_valid():
            orderitem.instance = self.object
            orderitem.save()
        return super().form_valid(form)
    def get_success_url(self):
        return reverse("admin-dashboard", 1)

# def create_order_with_items(request, event_id):
#     template_name = 'bourse/create_with_item.html'
#     if request.method == 'GET':
#         orderform = OrderModelForm(request.GET or None)
#         formset = OrderItemFormset(queryset=OrderItem.objects.none())
#     elif request.method == 'POST':
#         orderform = OrderModelForm(request.POST)
#         formset = OrderItemFormset(request.POST)
#         if orderform.is_valid() and formset.is_valid():
#             # first save this order, as its reference will be used in `Author`
#             order = orderform.save()
#             for form in formset:
#                 # so that `order` instance can be attached.
#                 orderitem = form.save(commit=False)
#                 orderitem.order = order
#                 orderitem.save()
#             return redirect('dashboard', 1)
#     return render(request, template_name, {
#         'orderform': orderform,
#         'formset': formset,
#     })