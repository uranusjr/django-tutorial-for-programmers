# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=20)),
                ('price', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=20)),
                ('notes', models.TextField(default='', blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='menuitem',
            name='store',
            field=models.ForeignKey(to='stores.Store', related_name='menu_items'),
        ),
    ]
