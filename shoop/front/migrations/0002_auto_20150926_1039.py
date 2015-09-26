# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import shoop.core.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shoop', '0009_auto_20150926_1039'),
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
        migrations.RenameField(
            model_name='storedbasket',
            old_name='owner_contact',
            new_name='customer',
        ),
        migrations.AlterField(
            model_name='storedbasket',
            name='customer',
            field=models.ForeignKey(blank=True, null=True, to='shoop.Contact', related_name='customer_baskets'),
        ),
        migrations.RenameField(
            model_name='storedbasket',
            old_name='owner_user',
            new_name='creator',
        ),
        migrations.AlterField(
            model_name='storedbasket',
            name='creator',
            field=models.ForeignKey(blank=True, null=True, to=settings.AUTH_USER_MODEL, related_name='baskets_created'),
        ),
        migrations.AddField(
            model_name='storedbasket',
            name='currency',
            field=shoop.core.fields.CurrencyField(max_length=4, default=settings.SHOOP_HOME_CURRENCY),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='storedbasket',
            name='orderer',
            field=models.ForeignKey(blank=True, null=True, to='shoop.PersonContact', related_name='orderer_baskets'),
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
            field=models.ForeignKey(to='shoop.Shop', default=1),
            preserve_default=False,
        ),
    ]
