# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
from shoop.core.pricing import TaxfulPrice, TaxlessPrice


class TaxedPrice(object):
    """
    Price with calculated taxes.

    .. attribute:: taxful

       (`~shoop.core.pricing.TaxfulPrice`)
       Price including taxes.

    .. attribute:: taxless

       (`~shoop.core.pricing.TaxlessPrice`)
       Pretax price.

    .. attribute:: taxes

       (`list[shoop.core.taxing.LineTax]`)
       List of taxes applied to the price.
    """

    @classmethod
    def from_price_and_taxes(cls, price, taxes):
        zero = price.new(0).amount
        tax_amount = sum((x.amount for x in taxes), zero)
        if price.includes_tax:
            taxful = price
            taxless = TaxlessPrice(price.amount - tax_amount)
        else:
            taxful = TaxfulPrice(price.amount + tax_amount)
            taxless = price
        return cls(taxful, taxless, taxes)

    def __init__(self, taxful, taxless, taxes=None):
        """
        Initialize from given prices and taxes.

        :type taxful: shoop.core.pricing.TaxfulPrice
        :param taxful: Price including taxes.
        :type taxless: shoop.core.pricing.TaxlessPrice
        :param taxless: Pretax price.
        :type taxes: list[shoop.core.taxing.LineTax]|None
        :param taxes: List of taxes applied to the price.
        """
        assert isinstance(taxful, TaxfulPrice)
        assert isinstance(taxless, TaxlessPrice)

        self.taxful = taxful
        self.taxless = taxless
        self.taxes = taxes or []

        # Validation
        expected_taxful_amount = taxless.amount + self.tax_amount
        assert abs(taxful.amount - expected_taxful_amount).value < 0.00001

    @property
    def tax_amount(self):
        """
        Total amount of applied taxes.
        """
        zero = self.taxful.new(0).amount
        return sum((x.amount for x in self.taxes), zero)

    @property
    def tax_rate(self):
        """
        Tax rate calculated from taxful and taxless amounts.
        """
        return (self.taxful.amount / self.taxless.amount) - 1
