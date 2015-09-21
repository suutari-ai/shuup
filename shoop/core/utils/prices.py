# This file is part of Shoop.
#
# Copyright (c) 2012-2015, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
import decimal

from shoop.core.pricing import TaxfulPrice, TaxlessPrice


class LinePriceMixin(object):
    """
    Define line price properties by others.

    Needs quantity, unit_price, total_discount and total_tax_amount
    properties.

    The unit_price and total_discount must have compatible types.

    Invariants (excluding type conversions):
      * total_price = unit_price * quantity - total_discount
      * taxful_total_price = taxless_total_price + total_tax_amount
      * tax_rate = (taxful_total_price / taxless_total_price) - 1
      * tax_percentage = 100 * tax_rate
    """
    @property
    def total_price(self):
        """
        :rtype: shoop.core.pricing.Price
        """
        return self.unit_price * self.quantity - self.total_discount

    @property
    def taxful_total_price(self):
        """
        :rtype: TaxfulPrice
        """
        total = self.total_price
        if total.includes_tax:
            return total
        else:
            total_and_tax = total.amount + self.total_tax_amount
            return TaxfulPrice(total_and_tax.value, total.currency)

    @property
    def taxless_total_price(self):
        """
        :rtype: TaxlessPrice
        """
        total = self.total_price
        if total.includes_tax:
            total_without_tax = total.amount - self.total_tax_amount
            return TaxlessPrice(total_without_tax.value, total.currency)
        else:
            return total

    @property
    def tax_rate(self):
        """
        :rtype: decimal.Decimal
        """
        taxless_total = self.taxless_total_price
        taxful_total = self.taxful_total_price
        if not taxless_total.amount:
            return decimal.Decimal(0)
        return (taxful_total.amount / taxless_total.amount) - 1

    @property
    def tax_percentage(self):
        """
        :rtype: decimal.Decimal
        """
        return self.tax_rate * 100

    @property
    def taxful_unit_price(self):
        """
        :rtype: TaxfulPrice
        """
        unit_price = self.unit_price
        if unit_price.includes_tax:
            return unit_price
        else:
            value = unit_price.value * (1 + self.tax_rate)
            return TaxfulPrice(value, unit_price.currency)

    @property
    def taxless_unit_price(self):
        """
        :rtype: TaxlessPrice
        """
        unit_price = self.unit_price
        if unit_price.includes_tax:
            value = unit_price.value / (1 + self.tax_rate)
            return TaxlessPrice(value, unit_price.currency)
        else:
            return unit_price

    @property
    def taxful_total_discount(self):
        """
        :rtype: TaxfulPrice
        """
        total_discount = self.total_discount
        if total_discount.includes_tax:
            return total_discount
        else:
            value = total_discount.value * (1 + self.tax_rate)
            return TaxfulPrice(value, total_discount.currency)

    @property
    def taxless_total_discount(self):
        """
        :rtype: TaxlessPrice
        """
        total_discount = self.total_discount
        if total_discount.includes_tax:
            return TaxlessPrice(self.total_discount.amount / (1 + self.tax_rate))
        else:
            return total_discount
