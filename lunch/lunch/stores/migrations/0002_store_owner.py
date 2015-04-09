# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('stores', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='owner',
            field=models.ForeignKey(null=True, related_name='owned_stores', to=settings.AUTH_USER_MODEL),
        ),
    ]
