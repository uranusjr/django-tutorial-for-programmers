from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models


class Store(models.Model):

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, related_name='owned_stores',
    )
    name = models.CharField(max_length=20)
    notes = models.TextField(blank=True, default='')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store_detail', kwargs={'pk': self.pk})


class MenuItem(models.Model):

    store = models.ForeignKey('Store', related_name='menu_items')
    name = models.CharField(max_length=20)
    price = models.IntegerField()

    def __str__(self):
        return self.name
