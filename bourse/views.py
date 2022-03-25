# Django Imports
from django.shortcuts import get_object_or_404,render,redirect
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, FileResponse
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.db.models import Sum
from django.contrib.messages.views import SuccessMessageMixin
# Sys
import datetime, io
# Other Django imports
from .models import Event, UserList, Item, Order, OrderItem, Page
from django.contrib.auth.models import User
from .forms import UserForm, ItemForm, ListValidateForm, EventForm, OrderModelForm, OrderItemFormset, ItemTextForm, ListManageForm, InvoiceClientForm
from .printing import MyPrint

#############
### Index ###
#############
def index(request):
    opened_registration_event = Event.objects.filter(status=1)
    index_content = get_object_or_404(Page,id=1)
    context = {
        'opened_registration_event': opened_registration_event,
        'index_content': index_content,
    }
    return render(request, 'index.html', context=context)

##########################
### Profil Utilisateur ###
##########################
class ProfileUpdate(LoginRequiredMixin,SuccessMessageMixin,UpdateView):
    model = User
    form_class = UserForm
    template_name = 'bourse/profile_edit.html'
    success_message = "Profil mis a jour."
    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.id)
    def get_success_url(self):
        return reverse('bourse:profile-edit',kwargs={'pk':self.object.pk})

#######################
### Vues Événements ###
#######################

class EventListView(generic.ListView):
    model = Event

class EventDetailView(generic.DetailView):
    model = Event

###########################
### Vues sur les listes ###
###########################

# Création d'une liste si elle n'existe pas pour l'utilisateur
@login_required
def user_list_create_or_view(request, event_id):
    event_inst = get_object_or_404(Event,id=event_id,status=1)
    user_list = UserList.objects.get_or_create(event=event_inst,user=request.user)
    return redirect('bourse:my-list-view',user_list[0].pk)

# Listes de l'utilisateur
class ListsByUserListView(LoginRequiredMixin,generic.ListView):
    model = UserList
    template_name = 'bourse/lists_by_user.html'
    paginate_by = 5
    def get_queryset(self):
        return UserList.objects.filter(user=self.request.user).order_by('-created_date')

# Detail liste de l'utilisateur
class ListDetailByUserDetailView(LoginRequiredMixin,generic.DetailView):
    model = UserList
    template_name = 'bourse/list_detail_by_user.html'
    def get_queryset(self):
        return UserList.objects.filter(user=self.request.user).order_by('created_date')
    def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       user_list_items = Item.objects.filter(list=self.object,is_sold=True)
       context['nb_sold'] = user_list_items.count()
       context['total_vente'] = sum( int(item.price) - settings.COMMISSION for item in user_list_items)
       return context

# Validation de la liste par l'utilisateur (liste de status editable / Bourse en saisie ouverte)
@login_required
def ListValidate(request,pk):
    list_instance = get_object_or_404(UserList,pk=pk,user=request.user,list_status=1,event__status=1)
    success_url = redirect('bourse:my-list-view',list_instance.pk)
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

######################################
### Vues sur les éléments de liste ###
######################################

# Ajout d'un jeu à la liste de l'utilisateur
class ItemCreate(LoginRequiredMixin,CreateView):
    model = Item
    form_class = ItemForm
    def get_queryset(self):
        return Item.objects.filter(list=self.kwargs.get('list_id'),list__user=self.request.user,list__list_status=1,list__event__status=1)
    def form_valid(self, form):
        form.instance.list__user = self.request.user
        self.object = form.save(commit=False)
        self.object.list_id = self.kwargs.get('list_id', None)
        if UserList.objects.filter(user=self.request.user,id=self.object.list_id,list_status=1,event__status=1):
            self.object.save()
            return redirect('bourse:my-list-view',self.object.list_id)
        else:
            return HttpResponseForbidden()

# Mise à jour d'un jeu à la liste de l'utilisateur
class ItemUpdate(LoginRequiredMixin,UpdateView):
    model = Item
    form_class = ItemForm
    def get_queryset(self):
        return Item.objects.filter(id=self.kwargs.get('pk'),list__user=self.request.user,list__list_status=1,list__event__status=1)
    def form_valid(self, form):
        form.instance.list__user = self.request.user
        self.object = form.save(commit=False)
        self.object.list_id = self.kwargs.get('list_id', None)
        if UserList.objects.filter(user=self.request.user,id=self.object.list_id,list_status=1,event__status=1):
            self.object.save()
            return redirect('bourse:my-list-view',self.object.list_id)
        else:
            return HttpResponseForbidden()

# Suppression d'un jeu à la liste de l'utilisateur
class ItemDelete(LoginRequiredMixin,DeleteView):
    model = Item
    def get_queryset(self):
        return Item.objects.filter(id=self.kwargs.get('pk'),list__user=self.request.user,list__list_status=1,list__event__status=1)
    def get_success_url(self):
        return reverse_lazy('bourse:my-list-view',kwargs={'pk':self.kwargs.get('list_id','')})
    def post(self, request, *args, **kwargs):
        if "cancel" in request.POST:
            url = self.get_success_url()
            return HttpResponseRedirect(url)
        else:
            return super(ItemDelete, self).post(request, *args, **kwargs)

######################
### Administration ###
######################

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
        item_sold = Item.objects.filter(list__event=event_id,is_sold=True)
        item_sold_total = item_sold.count()
        item_sold_price_total = sum( int(item.price) for item in item_sold )
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
            'item_sold_price_total':item_sold_price_total,
            'order_total':order_total,
            'order_unvalidated':order_unvalidated
        }
        return render(request, 'bourse/admin_dashboard.html', context=context)
    else:
        return HttpResponseForbidden()

# Mise à jour du status d'un événement
class EventUpdate(UserPassesTestMixin,UpdateView):
    model = Event
    form_class = EventForm
    def test_func(self):
        return self.request.user.is_staff
    def get_queryset(self):
        return Event.objects.filter(id=self.kwargs.get('pk'))
    def form_valid(self, form):
        if self.request.user.is_staff == 1:
            self.object.save()
            return redirect('bourse:admin-dashboard',self.kwargs.get('pk'))
        else:
            return HttpResponseForbidden()

# Visualisation des listes des utilisateurs
class ListsListView(UserPassesTestMixin,generic.ListView):
    model = UserList
    template_name = 'bourse/admin_manage_lists.html'
    def test_func(self):
        return self.request.user.is_staff
    def get_queryset(self):
        return UserList.objects.filter(event=self.kwargs.get('pk')).order_by('validated_date')

# Generation de PDF de la liste de l'utilisateur
@login_required
def ListDetailPdfGen(request,event_id,list_id,var):
    event = get_object_or_404(Event,pk=event_id)
    user_list = get_object_or_404(UserList,pk=list_id,event=event_id)
    user_list_items = Item.objects.filter(list=list_id)
    filename = 'EVT_' + str(event_id) + '_LST_'+ str(list_id) + '.pdf'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=' + filename
    if var=='post':
        post=True
    elif var=='pre':
        post=False
    else:
        return HttpResponseForbidden()
    if request.user.is_staff == 1:
        buffer = io.BytesIO()
        report = MyPrint(buffer, 'A4')
        pdf = report.createDoc(event,user_list,user_list_items,post=post)
        response.write(pdf)
        return response
    else:
        return HttpResponseForbidden()


# Visu et changement de status d'une liste
@login_required
def ListDetailValidate(request,event_id,list_id):
    template_name = 'bourse/admin_list_validate.html'
    user_list = get_object_or_404(UserList,pk=list_id,event=event_id)
    user_list_items = Item.objects.filter(list=list_id)
    user_list_number_sold = user_list_items.filter(is_sold=True).count()
    user_list_total_sold = sum( int(item.price) for item in user_list_items.filter(is_sold=True) )
    user_list_total_sold_minus_com = sum( int(item.price) - settings.COMMISSION for item in user_list_items.filter(is_sold=True) )
    success_url = redirect('bourse:admin-lists-manage',event_id)
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
                'user_list_items':user_list_items,
                'total_sold':user_list_total_sold,
                'number_sold':user_list_number_sold,
                'total_sold_minus_com':user_list_total_sold_minus_com}
            return render(request,template_name,context)
    else:
        return HttpResponseForbidden()

#################
### Commandes ###
#################

# Création de commande vide
@login_required
def order_create(request, event_id):
    if request.user.is_staff == 1:
        event_inst = get_object_or_404(Event,id=event_id,status=3)
        order = Order.objects.create(event=event_inst)
        return redirect('bourse:admin-ordermanage', event_id, order.pk)
    else:
        return HttpResponseForbidden()

# Détail commande avec formulaire d'ajout de jeu
@login_required
def OrderDetailValidate(request,event_id,order_id):
    template_name = 'bourse/admin_order_detail.html'
    order = get_object_or_404(Order,pk=order_id,event=event_id)
    order_items = OrderItem.objects.filter(order=order_id)
    order_total = sum( int(item.item.price) for item in order_items )
    success_url = redirect('bourse:admin-orders',event_id)
    if request.user.is_staff == 1:
        if request.method == 'POST':
            if "cancel" in request.POST:
                return success_url
            elif "add_item" in request.POST:
                form_item = ItemTextForm(request.POST)
                if form_item.is_valid():
                    order_item_pk = form_item.clean_item_pk()
                    if Item.objects.filter(pk=order_item_pk,list__list_status=3,is_sold=False,list__event=event_id).exists():
                        item = Item.objects.get(pk=order_item_pk)
                        OrderItem.objects.create(order=order,item=item)
                    return HttpResponseRedirect("")
                else:
                    return HttpResponseRedirect("")
            else:
                form = OrderModelForm(request.POST)
                if form.is_valid():
                    order.is_validated = form.cleaned_data['is_validated']
                    for order_item in order_items:
                        if order.is_validated: # modifier les item de la commande is_sold et date sold
                            order_item.item.is_sold = True
                            order_item.item.sold_date = datetime.datetime.now()
                            order_item.item.save()
                        else: # nettoyer le is_sold et date_sold
                            order_item.item.is_sold = False
                            order_item.item.sold_date = None
                            order_item.item.save()
                    order.save()
                    return success_url
        else:
            form = OrderModelForm(initial={'is_validated':order.is_validated})
            form_item = ItemTextForm()
            context = { 
                'form':form,
                'form_item':form_item,
                'order':order,
                'event_id':event_id,
                'order_items':order_items,
                'order_total':order_total,}
            return render(request,template_name,context)
    else:
        return HttpResponseForbidden()

# Supression d'un item de la commande en cours
class OrderItemDelete(UserPassesTestMixin,DeleteView):
    model = OrderItem
    def test_func(self):
        return self.request.user.is_staff
    def get_queryset(self):
        return OrderItem.objects.filter(id=self.kwargs.get('pk'),order__is_validated=False,order__event__status=3)
    def get_success_url(self):
        return reverse_lazy('bourse:admin-ordermanage',kwargs={'event_id':self.kwargs.get('event_id',''),'order_id':self.kwargs.get('order_id','')})
    def post(self, request, *args, **kwargs):
        if "cancel" in request.POST:
            url = self.get_success_url()
            return HttpResponseRedirect(url)
        else:
            return super(OrderItemDelete, self).post(request, *args, **kwargs)

# Formulaire avant facture pdf : détail client
@login_required
def OrderPreInvoicePdfGen(request,event_id,order_id):
    template_name = 'bourse/admin_order_pre_invoice_form.html'
    event = get_object_or_404(Event,pk=event_id)
    order = get_object_or_404(Order,pk=order_id,event=event_id)
    order_items = OrderItem.objects.filter(order=order_id)
    cancel_url = redirect('bourse:admin-orders',event_id)
    #success_url = redirect('admin-order-invoice-pdf',event_id,order_id)
    filename = 'EVT_' + str(event_id) + '_INVOICE_'+ str(order_id) + '.pdf'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=' + filename
    if request.user.is_staff == 1:
        if request.method == 'POST':
            if "cancel" in request.POST:
                return cancel_url
            elif "validate" in request.POST:
                form = InvoiceClientForm(request.POST)
                if form.is_valid():
                    buffer = io.BytesIO()
                    report = MyPrint(buffer, 'A4')
                    pdf = report.createInvoice(event,order,order_items,form.cleaned_data)
                    response.write(pdf)
                    return response
                    ##OrderDetailPdfGen(request,event_id,order_id,self.data) # TO DO
                    ##return HttpResponseRedirect(reverse_lazy('admin-order-invoice-pdf',kwargs={'event_id':event_id,'order_id':order_id}))
        else:
            form = InvoiceClientForm()
            context = { 
                'form':form,
                'event':event,
                'order':order,
                'order_items':order_items}
            return render(request,template_name,context)
    else:
        return HttpResponseForbidden()

# Generation du pdf de Facture pour une vente
@login_required
def OrderDetailPdfGen(request,event_id,order_id,*args):
    event = get_object_or_404(Event,pk=event_id)
    order = get_object_or_404(Order,pk=order_id,event=event_id)
    order_items = OrderItem.objects.filter(order=order_id)
    filename = 'EVT_' + str(event_id) + '_INVOICE_'+ str(order_id) + '.pdf'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=' + filename
    if request.user.is_staff == 1:
        buffer = io.BytesIO()
        report = MyPrint(buffer, 'A4')
        pdf = report.createInvoice(event,order,order_items)
        response.write(pdf)
        return response
    else:
        return HttpResponseForbidden()

# Visualisation des commandes de la bourse
class OrdersListView(UserPassesTestMixin,generic.ListView):
    model = Order
    template_name = 'bourse/admin_orders_list.html'
    paginate_by = 5
    def test_func(self):
        return self.request.user.is_staff
    def get_queryset(self):
        return Order.objects.filter(event=self.kwargs.get('event_id')).order_by('-created_date')