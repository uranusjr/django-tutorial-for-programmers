# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0002_store_owner'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='menuitem',
            options={'verbose_name_plural': 'Menu items', 'verbose_name': 'Menu item'},
        ),
        migrations.AlterModelOptions(
            name='store',
            options={'verbose_name_plural': 'Stores', 'verbose_name': 'Store'},
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='name',
            field=models.CharField(verbose_name='name', max_length=20),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='price',
            field=models.IntegerField(verbose_name='price'),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='store',
            field=models.ForeignKey(to='stores.Store', verbose_name='store', related_name='menu_items'),
        ),
        migrations.AlterField(
            model_name='store',
            name='name',
            field=models.CharField(verbose_name='name', max_length=20),
        ),
        migrations.AlterField(
            model_name='store',
            name='notes',
            field=models.TextField(verbose_name='notes', blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='store',
            name='owner',
            field=models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, verbose_name='owner', related_name='owned_stores'),
        ),
    ]
