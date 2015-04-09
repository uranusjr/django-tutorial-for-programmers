from tastypie import authentication, authorization, fields, resources

from .models import Store, MenuItem


class ReadOnlyAuthentication(authentication.Authentication):
    def is_authenticated(self, request, **kwargs):
        if request.method.lower() == 'get':
            return True
        return False


class MenuItemRelatedResource(resources.ModelResource):
    class Meta:
        queryset = MenuItem.objects.all()
        fields = ('name', 'price',)


class StoreResource(resources.ModelResource):

    menu_items = fields.ToManyField(
        to=MenuItemRelatedResource, attribute='menu_items', full=True,
    )

    class Meta:
        queryset = Store.objects.all()
        resource_name = 'store'
        authentication = authentication.MultiAuthentication(
            ReadOnlyAuthentication(),
            authentication.SessionAuthentication(),
        )
        authorization = authorization.DjangoAuthorization()


class MenuItemResource(resources.ModelResource):
    class Meta:
        queryset = MenuItem.objects.all()
        resource_name = 'stores/menu_item'
        list_allowed_methods = ('get', 'post',)
        detail_allowed_methods = ('post', 'put', 'delete', 'patch',)
        authentication = authentication.SessionAuthentication()
        authorization = authorization.DjangoAuthorization()
