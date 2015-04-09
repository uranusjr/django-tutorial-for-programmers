# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def create_stores(apps, schema_editor):
    Store = apps.get_model('stores', 'Store')
    MenuItem = apps.get_model('stores', 'MenuItem')
    Store.objects.create(name='肯德基', notes='沒有薄皮嫩雞倒一倒算了啦')

    mcdonalds = Store.objects.create(name='McDonalds')
    MenuItem.objects.create(store=mcdonalds, name='大麥克餐', price=99)
    MenuItem.objects.create(store=mcdonalds, name='蛋捲冰淇淋', price=15)


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0003_auto_20150409_1551'),
    ]

    operations = [
        migrations.RunPython(create_stores),
    ]
