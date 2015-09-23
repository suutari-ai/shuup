# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import shoop.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('shoop', '0007_auto_20150923_1513'),
        ('shoop_front', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='storedbasket',
            old_name='taxful_total',
            new_name='taxful_total_value',
        ),
        migrations.RenameField(
            model_name='storedbasket',
            old_name='taxless_total',
            new_name='taxless_total_value',
        ),
        migrations.AddField(
            model_name='storedbasket',
            name='currency',
            field=shoop.core.fields.CurrencyField(max_length=4, default='EUR'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='storedbasket',
            name='shop',
            field=models.ForeignKey(to='shoop.Shop', default=1),
            preserve_default=False,
        ),
    ]
