# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shoop', '0008_remove_payment_currency'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='purchase_price',
        ),
        migrations.RemoveField(
            model_name='product',
            name='suggested_retail_price',
        ),
        migrations.RemoveField(
            model_name='suppliedproduct',
            name='purchase_price',
        ),
        migrations.RemoveField(
            model_name='suppliedproduct',
            name='suggested_retail_price',
        ),
    ]
