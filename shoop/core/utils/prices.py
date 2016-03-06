# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
from shoop.core.pricing import Priceful, PriceInfo
from shoop.core.taxing import (
    get_tax_module, should_calculate_taxes_automatically
)


def convert_taxness(request, item, priceful, with_taxes):
    """
    Convert taxness of a priceful object.

    Return a `Priceful` object ``result`` satisfying
    ``result.price.includes_tax == with_taxes`` if possible.

    When given `priceful` does not have tax amount and taxes cannot be
    calculated automatically (`should_calculate_taxes_automatically`
    returns false), return the given `priceful` as is.

    Given `request` is used for constructing a
    `~shoop.core.taxing.TaxingContext`.

    :type request: django.http.HttpRequest
    :type item: shoop.core.taxing.TaxableItem
    :type priceful: shoop.core.pricing.Priceful
    :type with_taxes: bool
    :rtype: shoop.core.pricing.Priceful
    """
    if priceful.price.includes_tax == with_taxes:
        return priceful

    taxed_priceful = _make_taxed(request, item, priceful, with_taxes)

    return taxed_priceful if taxed_priceful else priceful


def _make_taxed(request, item, priceful, with_taxes):
    """
    :type request: django.http.HttpRequest
    :type item: shoop.core.taxing.TaxableItem
    :type priceful: shoop.core.pricing.Priceful
    :rtype: shoop.core.pricing.Priceful|None
    """
    try:
        tax_amount = getattr(priceful, 'tax_amount', None)
    except TypeError:  # e.g. shoop.core.order_creator.TaxesNotCalculated
        tax_amount = None

    if tax_amount is not None:
        if with_taxes:
            return PriceInfo(
                priceful.taxful_price, priceful.taxful_base_price,
                quantity=priceful.quantity)
        else:
            return PriceInfo(
                priceful.taxless_price, priceful.taxless_base_price,
                quantity=priceful.quantity)

    if not should_calculate_taxes_automatically():
        return None

    taxmod = get_tax_module()
    taxctx = taxmod.get_context_from_request(request)
    taxed_price = taxmod.get_taxed_price_for(
        taxctx, item, priceful.price)
    taxed_base_price = taxmod.get_taxed_price_for(
        taxctx, item, priceful.base_price)

    if with_taxes:
        return PriceInfo(
            taxed_price.taxful, taxed_base_price.taxful,
            quantity=priceful.quantity)
    else:
        return PriceInfo(
            taxed_price.taxless, taxed_base_price.taxless,
            quantity=priceful.quantity)

'''
class _TaxedPriceful(Priceful):
    price = None
    base_price = None

    def __init__(self, priceful, tax_amount, base_tax_amount):
        """
        :type priceful: Priceful
        :type tax_amount: shoop.utils.money.Money
        :type base_tax_amount: shoop.utils.money.Money
        """
        self.price = priceful.price
        self.base_price = priceful.base_price
        self.quantity = priceful.quantity
        self.tax_amount = tax_amount

    def __repr__(self):
        return '<%s price=%r, base_price=%r, tax_amount=%r>' % (
            type(self).__name__, self.price, self.base_price, self.tax_amount)


class TaxfulPriceful(Priceful):
    price = None
    base_price = None

    def __init__(self, original):
        """
        :type original: Priceful
        """
        self.price = original.taxful_price
        self.base_price = original.taxful_base_price
        self.quantity = original.quantity
        self.tax_amount = original.tax_amount


class TaxlessPriceful(Priceful):
    price = None
    base_price = None

    def __init__(self, original):
        """
        :type original: Priceful
        """
        self.price = original.taxless_price
        self.base_price = original.taxless_base_price
        self.quantity = original.quantity
        self.tax_amount = original.tax_amount
'''
