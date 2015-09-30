# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import shoop.core.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shoop', '0009_auto_20150930_0429'),
        ('shoop_front', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='storedbasket',
            old_name='taxful_total',
            new_name='taxful_total_price_value',
        ),
        migrations.RenameField(
            model_name='storedbasket',
            old_name='taxless_total',
            new_name='taxless_total_price_value',
        ),
        migrations.RemoveField(
            model_name='storedbasket',
            name='owner_contact',
        ),
        migrations.RemoveField(
            model_name='storedbasket',
            name='owner_user',
        ),
        migrations.AddField(
            model_name='storedbasket',
            name='creator',
            field=models.ForeignKey(null=True, blank=True, to=settings.AUTH_USER_MODEL, related_name='baskets_created'),
        ),
        migrations.AddField(
            model_name='storedbasket',
            name='currency',
            field=shoop.core.fields.CurrencyField(max_length=4, default='EUR'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='storedbasket',
            name='customer',
            field=models.ForeignKey(null=True, blank=True, to='shoop.Contact', related_name='customer_baskets'),
        ),
        migrations.AddField(
            model_name='storedbasket',
            name='orderer',
            field=models.ForeignKey(null=True, blank=True, to='shoop.PersonContact', related_name='orderer_baskets'),
        ),
        migrations.AddField(
            model_name='storedbasket',
            name='prices_include_tax',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='storedbasket',
            name='shop',
            field=models.ForeignKey(default=1, to='shoop.Shop'),
            preserve_default=False,
        ),
    ]
