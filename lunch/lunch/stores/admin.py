from django.contrib import admin
from .models import Store, MenuItem


class MenuItemInline(admin.StackedInline):
    model = MenuItem
    extra = 1


class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'notes',)
    inlines = (MenuItemInline,)


class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price',)


admin.site.register(Store, StoreAdmin)
admin.site.register(MenuItem, MenuItemAdmin)
