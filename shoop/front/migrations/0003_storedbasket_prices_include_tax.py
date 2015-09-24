# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shoop_front', '0002_auto_20150923_1513'),
    ]

    operations = [
        migrations.AddField(
            model_name='storedbasket',
            name='prices_include_tax',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
    ]
