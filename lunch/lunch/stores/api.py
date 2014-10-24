from rest_framework import mixins, permissions, serializers, viewsets
from .models import Store, MenuItem


class MenuItemRelatedSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ('name', 'price',)


class StoreSerializer(serializers.ModelSerializer):

    menu_items = MenuItemRelatedSerializer(many=True)

    class Meta:
        model = Store


class StoreViewSet(viewsets.ModelViewSet):
    model = Store
    serializer_class = StoreSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class MenuItemViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin, viewsets.GenericViewSet):
    model = MenuItem
