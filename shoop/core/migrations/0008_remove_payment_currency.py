# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shoop', '0007_auto_20150923_1513'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='currency',
        ),
    ]
