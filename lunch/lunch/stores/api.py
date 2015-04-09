from rest_framework import mixins, permissions, serializers, viewsets
from .models import Store, MenuItem


class MenuItemRelatedSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ('name', 'price',)


class MenuItemViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = MenuItem.objects.all()


class StoreSerializer(serializers.ModelSerializer):

    menu_items = MenuItemRelatedSerializer(many=True)

    class Meta:
        model = Store


class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
