from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.views.generic import CreateView, DetailView
from braces.views import LoginRequiredMixin
from .models import Event, Order
from .forms import EventForm, OrderForm


class EventCreateView(LoginRequiredMixin, CreateView):

    model = Event
    form_class = EventForm
    http_method_names = ('post',)


class EventDetailView(LoginRequiredMixin, DetailView):

    model = Event

    def get_order(self, user):
        try:
            order = Order.objects.get(user=user, event=self.get_object())
        except Order.DoesNotExist:
            order = None
        return order

    def post(self, request, *args, **kwargs):
        order = self.get_order(user=request.user)
        form = OrderForm(request.POST, instance=order)
        if not form.is_valid():
            return HttpResponseBadRequest()
        order = form.save(commit=False)
        order.user = request.user
        order.event = self.get_object()
        order.save()
        return redirect(order.event.get_absolute_url())

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        order = self.get_order(user=self.request.user)
        order_form = OrderForm(instance=order)
        order_form.fields['item'].queryset = self.object.store.menu_items.all()
        data['order_form'] = order_form
        return data
