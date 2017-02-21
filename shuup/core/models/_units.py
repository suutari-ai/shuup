# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2017, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import unicode_literals

from decimal import Decimal

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.translation import pgettext, ugettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields

from shuup.core.fields import InternalIdentifierField
from shuup.utils.i18n import format_number
from shuup.utils.numbers import bankers_round, parse_decimal_string


__all__ = ("SalesUnit",)


@python_2_unicode_compatible
class SalesUnit(TranslatableModel):
    identifier = InternalIdentifierField(unique=True)
    decimals = models.PositiveSmallIntegerField(default=0, verbose_name=_(u"allowed decimal places"), help_text=_(
        "The number of decimal places allowed by this sales unit."
        "Set this to a value greater than zero if products with this sales unit can be sold in fractional quantities"
    ))
    
    translations = TranslatedFields(
        name=models.CharField(max_length=128, verbose_name=_('name'), help_text=_(
            "The sales unit name to use for products (For example, 'pieces' or 'units'). "
            "Sales units can be set for each product through the product editor view."
        )),
        short_name=models.CharField(max_length=128, verbose_name=_('short name'), help_text=_(
            "An abbreviated name for this sales unit that is shown throughout admin and order invoices."
        )),
    )

    class Meta:
        verbose_name = _('sales unit')
        verbose_name_plural = _('sales units')

    def __str__(self):
        return self.safe_translation_getter("name", default=self.identifier) or ""

    @property
    def base_quantity(self):
        if self.short_name == "kg":  # test kg -> 100 g conversion
            return Decimal('0.1')  # 0.1 kg (i.e. 100 g)
        return 1

    def display_short_name(self):
        if self.short_name == "kg":  # test kg -> 100 g conversion
            return "g"
        return self.short_name

    @property
    def display_factor(self):
        if self.short_name == "kg":  # test kg -> 100 g conversion
            return 1000  # 1000 g = 1 kg
        return 1

    @property
    def display_decimals(self):
        if self.short_name == "kg":  # test kg -> 100 g conversion
            return 0
        return self.decimals

    @property
    def allow_fractions(self):
        return self.decimals > 0

    @cached_property
    def quantity_step(self):
        """
        Get the quantity increment for the amount of decimals this unit allows.

        For 0 decimals, this will be 1; for 1 decimal, 0.1; etc.

        :return: Decimal in (0..1]
        :rtype: Decimal
        """

        # This particular syntax (`10 ^ -n`) is the same that `bankers_round` uses
        # to figure out the quantizer.

        return Decimal(10) ** (-int(self.decimals))

    def round(self, value):
        return bankers_round(parse_decimal_string(value), self.decimals)

    def display(self, value):
        converted = value * self.display_factor
        rounded = bankers_round(converted, self.display_decimals)
        pgettext('display value with unit', "{value}{unit}").format(
            value=format_number(rounded),
            unit=self.display_short_name)
