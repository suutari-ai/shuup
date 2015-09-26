# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import shoop.core.models.shops
import shoop.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('shoop', '0008_maintenance_mode'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='taxful_total_price',
            new_name='taxful_total_price_value',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='taxless_total_price',
            new_name='taxless_total_price_value',
        ),
        migrations.RenameField(
            model_name='orderline',
            old_name='_total_discount_amount',
            new_name='total_discount_value',
        ),
        migrations.RenameField(
            model_name='orderline',
            old_name='_unit_price_amount',
            new_name='unit_price_value',
        ),
        migrations.RenameField(
            model_name='orderlinetax',
            old_name='amount',
            new_name='amount_value',
        ),
        migrations.RenameField(
            model_name='orderlinetax',
            old_name='base_amount',
            new_name='base_amount_value',
        ),
        migrations.RenameField(
            model_name='payment',
            old_name='amount',
            new_name='amount_value',
        ),
        migrations.RenameField(
            model_name='shopproduct',
            old_name='default_price',
            new_name='default_price_value',
        ),
        migrations.RenameField(
            model_name='tax',
            old_name='amount',
            new_name='amount_value',
        ),
        migrations.RemoveField(
            model_name='orderline',
            name='_prices_include_tax',
        ),
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
        migrations.AddField(
            model_name='order',
            name='currency',
            field=shoop.core.fields.CurrencyField(max_length=4, default=settings.SHOOP_HOME_CURRENCY),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='prices_include_tax',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='payment',
            name='foreign_amount_value',
            field=shoop.core.fields.MoneyValueField(null=True, decimal_places=9, default=None, max_digits=36, blank=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='foreign_currency',
            field=shoop.core.fields.CurrencyField(null=True, max_length=4, default=None, blank=True),
        ),
        migrations.AddField(
            model_name='shop',
            name='currency',
            field=shoop.core.fields.CurrencyField(max_length=4, default=shoop.core.models.shops._get_default_currency),
        ),
        migrations.AddField(
            model_name='tax',
            name='currency',
            field=shoop.core.fields.CurrencyField(null=True, max_length=4, default=None, blank=True),
        ),
        migrations.AlterField(
            model_name='contact',
            name='tax_group',
            field=models.ForeignKey(blank=True, null=True, to='shoop.CustomerTaxGroup'),
        ),
        migrations.AlterField(
            model_name='order',
            name='display_currency',
            field=shoop.core.fields.CurrencyField(blank=True, max_length=4),
        ),
        migrations.AlterField(
            model_name='shop',
            name='prices_include_tax',
            field=models.BooleanField(default=False),
        ),
    ]
