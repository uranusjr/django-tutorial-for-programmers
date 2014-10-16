from django.contrib import admin
from .models import Event, Order


class OrderInline(admin.StackedInline):
    model = Order
    extra = 1


class EventAdmin(admin.ModelAdmin):
    inlines = (OrderInline,)


class OrderAdmin(admin.ModelAdmin):
    list_display = ('event', 'item', 'user',)


admin.site.register(Event, EventAdmin)
admin.site.register(Order, OrderAdmin)
