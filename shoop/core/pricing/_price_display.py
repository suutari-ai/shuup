# -*- coding: utf-8 -*-
# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
from django.utils.translation import ugettext_lazy as _
from enumfields import Enum


class PriceDisplayOption(Enum):
    HIDE_PRICES = 0
    DISPLAY_PRICES_AS_STORED = 1
    DISPLAY_TAXFUL_PRICES = 2
    DISPLAY_TAXLESS_PRICES = 3

    class Labels:
        HIDE_PRICES = _("Do not display prices for this group")
        DISPLAY_PRICES_AS_STORED = _("Display prices as stored in shop")
        DISPLAY_TAXFUL_PRICES = _("Display taxful prices")
        DISPLAY_TAXLESS_PRICES = _("Display taxless prices")


class PriceDisplayMode(object):
    def __init__(self, shop=None, option=PriceDisplayOption.HIDE_PRICES):
        self.hide_prices = (option == PriceDisplayOption.HIDE_PRICES)
        self.include_taxes = None
        if option == PriceDisplayOption.DISPLAY_PRICES_AS_STORED:
            self.include_taxes = shop.prices_include_tax
        else:
            self.include_taxes = (option == PriceDisplayOption.DISPLAY_TAXFUL_PRICES)
