# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shoop', '0020_services_and_methods'),
        ('campaigns', '0005_sales_ranges'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='BasketCampaign',
            new_name='CartCampaign',
        ),
        migrations.RenameModel(
            old_name='BasketCondition',
            new_name='CartCondition',
        ),
        migrations.RenameModel(
            old_name='BasketCampaignTranslation',
            new_name='CartCampaignTranslation',
        ),
        migrations.RenameModel(
            old_name='ContactBasketCondition',
            new_name='ContactCartCondition',
        ),
        migrations.RenameModel(
            old_name='ContactGroupBasketCondition',
            new_name='ContactGroupCartCondition',
        ),
        migrations.RenameModel(
            old_name='ProductsInBasketCondition',
            new_name='ProductsInCartCondition',
        ),
        migrations.RenameModel(
            old_name='BasketTotalAmountCondition',
            new_name='CartTotalAmountCondition',
        ),
        migrations.RenameModel(
            old_name='BasketTotalProductAmountCondition',
            new_name='CartTotalProductAmountCondition',
        ),
    ]
