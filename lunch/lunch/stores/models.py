from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Store(models.Model):

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, related_name='owned_stores',
        verbose_name=_('owner'),
    )
    name = models.CharField(
        max_length=20, verbose_name=_('name'),
    )
    notes = models.TextField(
        blank=True, default='', verbose_name=_('notes'),
    )

    class Meta:
        verbose_name = _('Store')
        verbose_name_plural = _('Stores')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store_detail', kwargs={'pk': self.pk})

    def can_user_delete(self, user):
        if not self.owner or self.owner == user:
            return True
        if user.has_perm('stores.delete_store'):
            return True
        return False


class MenuItem(models.Model):

    store = models.ForeignKey(
        'Store', related_name='menu_items', verbose_name=_('store'),
    )
    name = models.CharField(
        max_length=20, verbose_name=_('name'),
    )
    price = models.IntegerField(
        verbose_name=_('price'),
    )

    class Meta:
        verbose_name = _('Menu item')
        verbose_name_plural = _('Menu items')

    def __str__(self):
        return self.name
