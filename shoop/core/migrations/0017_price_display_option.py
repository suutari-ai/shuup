# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import enumfields.fields
import shoop.core.pricing


class Migration(migrations.Migration):

    dependencies = [
        ('shoop', '0016_shop_contact_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactgroup',
            name='price_display_option',
            field=enumfields.fields.EnumIntegerField(default=1, enum=shoop.core.pricing.PriceDisplayOption, verbose_name='price display option'),
        ),
    ]
