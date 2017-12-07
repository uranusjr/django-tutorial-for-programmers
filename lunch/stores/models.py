from django.db import models


class Store(models.Model):

    name = models.CharField(
        max_length=20,
    )
    notes = models.TextField(
        blank=True, default='',
    )

    def __str__(self):
        return self.name


class MenuItem(models.Model):

    store = models.ForeignKey(
        to=Store, on_delete=models.CASCADE, related_name='menuitem_set',
    )
    name = models.CharField(
        max_length=20,
    )
    price = models.IntegerField(
    )

    def __str__(self):
        return self.name
