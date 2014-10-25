import logging
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from events.forms import EventForm
from .forms import StoreForm, MenuItemFormSet
from .models import Store


logger = logging.getLogger(__name__)


def store_list(request):
    stores = Store.objects.all()
    return render(request, 'stores/store_list.html', {'stores': stores})


def store_detail(request, pk):
    try:
        store = Store.objects.get(pk=pk)
    except Store.DoesNotExist:
        raise Http404
    event_form = EventForm(initial={'store': store}, submit_title='建立活動')
    event_form.helper.form_action = reverse('event_create')
    return render(request, 'stores/store_detail.html', {
        'store': store, 'event_form': event_form,
    })


def store_create(request):
    if request.method == 'POST':
        form = StoreForm(request.POST)
        if form.is_valid():
            store = form.save(commit=False)
            if request.user.is_authenticated():
                store.owner = request.user
            store.save()
            logger.info('New store {store} created by {user}!'.format(
                store=store, user=request.user
            ))
            return redirect(store.get_absolute_url())
    else:
        form = StoreForm(submit_title='建立')
    return render(request, 'stores/store_create.html', {'form': form})


def store_update(request, pk):
    try:
        store = Store.objects.get(pk=pk)
    except Store.DoesNotExist:
        raise Http404
    if request.method == 'POST':
        form = StoreForm(request.POST, instance=store)
        menu_item_formset = MenuItemFormSet(request.POST, instance=store)
        if form.is_valid() and menu_item_formset.is_valid():
            store = form.save()
            menu_item_formset.save()
            return redirect(store.get_absolute_url())
    else:
        form = StoreForm(instance=store, submit_title=None)
        form.helper.form_tag = False
        menu_item_formset = MenuItemFormSet(instance=store)
    return render(request, 'stores/store_update.html', {
        'form': form, 'store': store, 'menu_item_formset': menu_item_formset,
    })


@login_required
@require_http_methods(['POST', 'DELETE'])
def store_delete(request, pk):
    try:
        store = Store.objects.get(pk=pk)
    except Store.DoesNotExist:
        raise Http404
    if store.can_user_delete(request.user):
        store.delete()
        if request.is_ajax():
            return HttpResponse()
        return redirect('store_list')
    return HttpResponseForbidden()
