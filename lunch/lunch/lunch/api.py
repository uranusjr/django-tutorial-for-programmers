from rest_framework import routers
from stores.api import StoreViewSet, MenuItemViewSet

v1 = routers.DefaultRouter()
v1.register(r'store', StoreViewSet)
v1.register(r'stores/menu_item', MenuItemViewSet)


from tastypie.api import Api
from stores.resources import StoreResource, MenuItemResource

v2 = Api(api_name='v2')
v2.register(StoreResource())
v2.register(MenuItemResource())
