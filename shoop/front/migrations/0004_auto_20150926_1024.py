# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shoop', '0011_auto_20150926_1024'),
        ('shoop_front', '0003_storedbasket_prices_include_tax'),
    ]

    operations = [
        migrations.RenameField(
            model_name='storedbasket',
            old_name='taxful_total_value',
            new_name='taxful_total_price_value',
        ),
        migrations.RenameField(
            model_name='storedbasket',
            old_name='taxless_total_value',
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
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True, related_name='baskets_created'),
        ),
        migrations.AddField(
            model_name='storedbasket',
            name='customer',
            field=models.ForeignKey(to='shoop.Contact', null=True, blank=True, related_name='customer_baskets'),
        ),
        migrations.AddField(
            model_name='storedbasket',
            name='orderer',
            field=models.ForeignKey(to='shoop.PersonContact', null=True, blank=True, related_name='orderer_baskets'),
        ),
    ]
