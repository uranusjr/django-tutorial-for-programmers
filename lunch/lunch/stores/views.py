from django.forms.models import modelform_factory
from django.http import Http404
from django.shortcuts import render, redirect
from .models import Store


def store_list(request):
    stores = Store.objects.all()
    return render(request, 'stores/store_list.html', {'stores': stores})


def store_detail(request, pk):
    try:
        store = Store.objects.get(pk=pk)
    except Store.DoesNotExist:
        raise Http404
    return render(request, 'stores/store_detail.html', {'store': store})


def store_create(request):
    StoreForm = modelform_factory(Store)
    if request.method == 'POST':
        form = StoreForm(request.POST)
        if form.is_valid():
            store = form.save()
            return redirect(store.get_absolute_url())
    else:
        form = StoreForm()
    return render(request, 'stores/store_create.html', {'form': form})


def store_update(request, pk):
    try:
        store = Store.objects.get(pk=pk)
    except Store.DoesNotExist:
        raise Http404
    StoreForm = modelform_factory(Store)
    if request.method == 'POST':
        form = StoreForm(request.POST, instance=store)
        if form.is_valid():
            store = form.save()
            return redirect(store.get_absolute_url())
    else:
        form = StoreForm(instance=store)
    return render(request, 'stores/store_update.html', {
        'form': form, 'store': store,
    })
