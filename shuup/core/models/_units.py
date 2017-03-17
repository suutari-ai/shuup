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
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext
from parler.models import TranslatedFields

from shuup.core.fields import InternalIdentifierField, QuantityField
from shuup.utils.i18n import format_number
from shuup.utils.numbers import bankers_round, parse_decimal_string

from ._base import TranslatableShuupModel


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
        return self.symbol

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
    is_countable = models.BooleanField(
        default=False, verbose_name=_(
            "countable"),
        help_text=_(
            "Values of countable units can be shown without the symbol "
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
        self.is_countable = (sales_unit.decimals == 0)
        self.default = False

    name = property(lambda self: self.internal_unit.name)
    symbol = property(lambda self: self.internal_unit.symbol)

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


class UnitInterface(object):
    """
    Interface to unit functions.

    Provides methods for rounding, rendering and converting product
    quantities in display unit or internal unit.
    """
    def __init__(self, internal_unit=None, display_unit=None):
        """
        Initialize unit interface.

        :type internal_unit: SalesUnit|PiecesSalesUnit
        :type display_unit: DisplayUnit|SalesUnitAsDisplayUnit
        """
        if display_unit:
            self.internal_unit = display_unit.internal_unit
            self.display_unit = display_unit
        else:
            self.internal_unit = internal_unit or PiecesSalesUnit()
            self.display_unit = self.internal_unit.display_unit
        assert self.display_unit.internal_unit == self.internal_unit

    @property
    def symbol(self):
        """
        Symbol of the display unit.

        :rtype: str
        """
        return self.display_unit.symbol or PiecesSalesUnit.symbol

    def get_symbol(self, allow_empty=True):
        """
        Get symbol of the display unit or empty if it is not needed.

        :rtype: str
        """
        if allow_empty and self.is_countable and (
                self.display_unit.comparison_value == 1):
            return ''
        return self.symbol

    @property
    def internal_symbol(self):
        """
        Symbol of the internal unit.

        :rtype: str
        """
        return self.internal_unit.symbol

    @property
    def is_countable(self):
        """
        Get countability of the display unit.

        :rtype: bool
        """
        return self.display_unit.is_countable

    def render_quantity(self, quantity, force_symbol=False):
        """
        Render (internal unit) quantity in the display unit.

        The value converted from the internal unit to the display unit
        and then localized.  The display unit symbol is added if needed.

        :type quantity: Decimal
        :param quantity: Quantity to render, in internal unit
        :type force_symbol: bool
        :param force_symbol: Make sure that the symbol is rendered
        :rtype: str
        :return: Rendered quantity in display unit.
        """
        display_quantity = self.to_display(quantity)
        value = format_number(display_quantity, self.display_unit.decimals)
        symbol = self.get_symbol(allow_empty=(not force_symbol))
        if not symbol:
            return value
        return _get_value_symbol_template().format(value=value, symbol=symbol)

    def render_quantity_internal(self, quantity, force_symbol=False):
        """
        Render quantity (in internal unit) in the internal unit.

        The value is localized and the internal unit symbol is added if
        needed.

        :type quantity: Decimal
        :param quantity: Quantity to render, in internal unit
        :type force_symbol: bool
        :param force_symbol: Make sure that the symbol is rendered
        :rtype: str
        :return: Rendered quantity in internal unit.
        """
        value = format_number(quantity, self.internal_unit.decimals)
        if not force_symbol and self.is_countable:
            return value
        symbol = self.internal_unit.symbol
        return _get_value_symbol_template().format(value=value, symbol=symbol)

    def to_display(self, quantity):
        """
        Convert quantity from internal unit to display unit.

        :type quantity: Decimal
        :param quantity: Quantity to convert, in internal unit
        :rtype: Decimal
        :return: Converted quantity, in display unit
        """
        rounded = _round_to_digits(Decimal(quantity), self.internal_unit.decimals)
        value = rounded / self.display_unit.ratio
        return _round_to_digits(value, self.display_unit.decimals)

    def from_display(self, display_quantity):
        """
        Convert quantity from display unit to internal unit.

        :type quantity: Decimal
        :param quantity: Quantity to convert, in display unit
        :rtype: Decimal
        :return: Converted quantity, in internal unit
        """
        converted = Decimal(display_quantity) * self.display_unit.ratio
        return _round_to_digits(converted, self.internal_unit.decimals)

    def get_per_values(self, force_symbol=False):
        """
        Get "per" quantity and "per" text according to the display unit.

        Useful when rendering unit prices, e.g.::

          (per_qty, per_text) = unit.get_per_values(force_symbol=True)
          price = product.get_price(quantity=per_qty)
          unit_price_text = _("{price} per {per_text}").format(
              price=price, per_text=per_text)

        :rtype: (Decimal, str)
        :return:
          Quantity (in internal unit) and text to use as the unit in
          unit prices
        """
        symbol = self.get_symbol(allow_empty=(not force_symbol))
        without_value = (self.display_unit.comparison_value == 1)
        per_qty = self.comparison_quantity
        per_text = (symbol if without_value else self.render_quantity(per_qty))
        return (per_qty, per_text)

    @property
    def comparison_quantity(self):
        """
        Quantity (in internal unit) to use as the unit in unit prices.

        :rtype: Decimal
        :return: Quantity, in internal unit
        """
        return self.from_display(self.display_unit.comparison_value)


def _get_value_symbol_template():
    return pgettext(
        "Display value with unit symbol (with or without space)",
        "{value}{symbol}")


def _round_to_digits(value, digits, rounding=ROUND_HALF_UP):
    precision = Decimal('1.' + ('1' * digits))
    return value.quantize(precision, rounding=rounding)
