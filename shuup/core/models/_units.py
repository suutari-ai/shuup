# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2017, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import unicode_literals

import warnings
from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.translation import pgettext, ugettext_lazy as _
from parler.models import TranslatedFields

from ._base import TranslatableShuupModel
from shuup.core.fields import InternalIdentifierField, QuantityField
from shuup.utils.i18n import format_number
from shuup.utils.numbers import bankers_round, parse_decimal_string


@python_2_unicode_compatible
class SalesUnit(TranslatableShuupModel):
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
        symbol=models.CharField(max_length=128, verbose_name=_("symbol"), help_text=_(
            "An abbreviated name for this sales unit that is shown "
            "throughout admin and order invoices.")),
    )

    class Meta:
        verbose_name = _('sales unit')
        verbose_name_plural = _('sales units')

    def __str__(self):
        return self.safe_translation_getter("name", default=self.identifier) or ""

    @property
    def short_name(self):
        warnings.warn(
            "unit.short_name is deprecated, use unit.symbol instead",
            DeprecationWarning)
        return self.internal_unit.symbol

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

    @property
    def display_unit(self):
        default_display_unit = self.display_units.filter(default=True).first()
        return default_display_unit or SalesUnitAsDisplayUnit(self)


def validate_positive_not_zero(value):
    if value <= 0:
        raise ValidationError(_("Value must be positive and non-zero"))


@python_2_unicode_compatible
class DisplayUnit(TranslatableShuupModel):
    internal_unit = models.ForeignKey(
        SalesUnit, related_name='display_units',
        verbose_name=_("internal unit"),
        help_text=_("The sales unit that this display unit is linked to."))
    ratio = QuantityField(
        default=1, validators=[validate_positive_not_zero],
        verbose_name=_("ratio"),
        help_text=_(
            "Amount of internal units in a display unit.  E.g. if "
            "internal unit is kilogram and display unit is gram, "
            "ratio is 0.001."))
    decimals = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("decimal places"),
        help_text=_(
            "The number of decimal places to use for values in the "
            "display unit.  The internal values are still rounded "
            "based on settings of the internal unit."))
    comparison_value = QuantityField(
        default=1, validators=[validate_positive_not_zero],
        verbose_name=_("comparison value"),
        help_text=_(
            "Value to use when displaying unit prices.  E.g. if the "
            "display unit is g and the comparison value is 100, then "
            "unit prices are shown per 100g, like: $2.95 per 100g."))
    allow_hiding_symbol = models.BooleanField(
        default=False, verbose_name=_(
            "values may be shown without the symbol"),
        help_text=_(
            "Allow showing values of the unit without the symbol "
            "occasionally.  Usually wanted if the unit is a Piece, "
            "i.e. showing just $5 rather than $5 per pc."))
    default = models.BooleanField(
        default=False, verbose_name=_("use by default"), help_text=_(
            "Use this display unit by default when displaying "
            "values of the internal unit."))
    translations = TranslatedFields(
        name=models.CharField(
            max_length=150, verbose_name=_("name"), help_text=_(
                "Name of the display unit, e.g. Grams.")),
        symbol=models.CharField(
            max_length=50, verbose_name=_("symbol"), help_text=_(
                "An abbreviated name of the display unit, e.g. 'g'.")),
    )

    class Meta:
        verbose_name = _("display unit")
        verbose_name_plural = _("display units")


@python_2_unicode_compatible
class SalesUnitAsDisplayUnit(object):
    def __init__(self, sales_unit):
        self.internal_unit = sales_unit
        self.ratio = Decimal(1)
        self.decimals = sales_unit.decimals
        self.comparison_value = Decimal(1)
        self.allow_hiding_symbol = True
        self.default = False

    @property
    def name(self):
        return self.internal_unit.name

    @property
    def symbol(self):
        return self.internal_unit.symbol

    def __str__(self):
        return force_text(self.name)


@python_2_unicode_compatible
class PiecesSalesUnit(object):
    """
    Object representing Pieces sales unit.

    Has same API as SalesUnit, but isn't a real model.
    """

    identifier = '_internal_pieces_unit'

    name = _("Pieces")
    symbol = pgettext("Symbol for pieces unit", "pc.")
    decimals = 0

    @property
    def display_unit(self):
        return SalesUnitAsDisplayUnit(self)

    def __str__(self):
        return force_text(self.name)


class UnitAccessor(object):
    """
    Accessor for unit functions.

    Provides methods for rounding, rendering and converting product
    quantities in this unit.

    Provides the following methods:
      * `allow_fractions`
      * `quantity_step`
      * `round`
      * `display_sumbol`
      * `display_quantity`
      * `to_display`
      * `from_display`
      * `comparison_quantity`
      * `per_values`
    """
    def __init__(self, internal_unit, display_unit=None):
        """
        Initialize unit accessor.

        :type internal_unit: SalesUnit
        :type display_unit: DisplayUnit
        """
        self.internal_unit = internal_unit
        self.display_unit = display_unit or internal_unit.display_unit

    @property
    def symbol(self):
        return self.internal_unit.symbol

    @property
    def display_symbol(self):
        return self.display_unit.symbol or PiecesSalesUnit.symbol

    def get_display_symbol(self, allow_empty=True):
        du = self.display_unit
        if allow_empty and du.allow_hiding_symbol:
            if du.comparison_value == 1 and du.decimals == 0:
                return ''
        return self.display_symbol

    def display_quantity(self, quantity, force_symbol=False):
        display_quantity = self.to_display(quantity)
        value = format_number(display_quantity, self.display_unit.decimals)
        symbol = self.get_display_symbol(allow_empty=(not force_symbol))
        if not symbol:
            return value
        return _get_value_symbol_template().format(value=value, symbol=symbol)

    def to_display(self, quantity):
        rounded = round_to_digits(Decimal(quantity), self.internal_unit.decimals)
        return rounded / self.display_unit.ratio

    def from_display(self, display_quantity):
        converted = Decimal(display_quantity) * self.display_unit.ratio
        return round_to_digits(converted, self.internal_unit.decimals)

    def display_per_values(self, force_symbol=False):
        if not self.get_display_symbol(allow_empty=(not force_symbol)):
            return (1, '')
        exact_unit = (self.display_unit.comparison_value == 1)
        cmp_qty = self.comparison_quantity
        text = (self.display_symbol if exact_unit
                else self.display_quantity(cmp_qty))
        return (cmp_qty, text)

    @property
    def comparison_quantity(self):
        return self.from_display(self.display_unit.comparison_value)


def _get_value_symbol_template():
    return pgettext(
        "Display value with unit symbol (with or without space)",
        "{value}{symbol}")


def round_to_digits(value, digits, rounding=ROUND_HALF_UP):
    precision = Decimal('1.' + ('1' * digits))
    return value.quantize(precision, rounding=rounding)
