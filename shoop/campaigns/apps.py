# -*- coding: utf-8 -*-
# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.

from django.db.models.signals import post_save

from shoop.apps import AppConfig
from shoop.campaigns.signal_handlers import update_customers_groups
from shoop.core.models import Payment


class CampaignAppConfig(AppConfig):
    name = "shoop.campaigns"
    verbose_name = "Shoop Campaigns"
    label = "campaigns"
    provides = {
        "admin_contact_group_form_part": [
            "shoop.campaigns.admin_module.form_parts:SalesRangesFormPart"
        ],
        "discount_module": [
            "shoop.campaigns.modules:CatalogCampaignModule"
        ],
        "order_source_modifier_module": [
            "shoop.campaigns.modules:CartCampaignModule"
        ],
        "admin_module": [
            "shoop.campaigns.admin_module:CampaignAdminModule",
        ],
        "campaign_catalog_filter": [
            "shoop.campaigns.models.catalog_filters:ProductTypeFilter",
            "shoop.campaigns.models.catalog_filters:ProductFilter",
            "shoop.campaigns.models.catalog_filters:CategoryFilter"
        ],
        "campaign_context_condition": [
            "shoop.campaigns.models.context_conditions:ContactGroupCondition",
            "shoop.campaigns.models.context_conditions:ContactCondition",
        ],
        "campaign_cart_condition": [
            "shoop.campaigns.models.cart_conditions:CartTotalProductAmountCondition",
            "shoop.campaigns.models.cart_conditions:CartTotalAmountCondition",
            "shoop.campaigns.models.cart_conditions:ProductsInCartCondition",
            "shoop.campaigns.models.cart_conditions:ContactGroupCartCondition",
            "shoop.campaigns.models.cart_conditions:ContactCartCondition",
        ]
    }

    def ready(self):
        post_save.connect(
            update_customers_groups,
            sender=Payment,
            dispatch_uid="contact_group_sales:update_customers_groups")
