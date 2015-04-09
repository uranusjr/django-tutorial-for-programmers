# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('stores', '0002_store_owner'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('store', models.ForeignKey(related_name='events', to='stores.Store')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('notes', models.TextField(blank=True, default='')),
                ('event', models.ForeignKey(related_name='orders', to='events.Event')),
                ('item', models.ForeignKey(related_name='orders', to='stores.MenuItem')),
                ('user', models.ForeignKey(related_name='orders', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='order',
            unique_together=set([('event', 'user')]),
        ),
    ]
