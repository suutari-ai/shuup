# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.


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
