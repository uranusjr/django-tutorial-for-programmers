from django.contrib import admin

from .models import Event, Order


class OrderInline(admin.StackedInline):
    model = Order
    extra = 1


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    inlines = (OrderInline,)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('event', 'item', 'user',)
