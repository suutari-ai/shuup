# -*- coding: utf-8 -*-
# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.

import numbers

from ._price import Price
from ._priceful import Priceful


class PriceInfo(Priceful):
    """
    Object for passing around pricing data of an item.
    """

    price = None
    base_price = None
    quantity = None

    def __init__(self, price, base_price, quantity, expires_on=None,
                 discounted_unit_price=None, base_unit_price=None):
        """
        Initialize PriceInfo with prices and other parameters.

        Prices can be taxful or taxless, but their types must match.

        :type price: Price
        :param price:
          Effective price for the specified quantity.
        :type base_price: Price
        :param base_price:
          Base price for the specified quantity.  Discounts are
          calculated based on this.
        :type quantity: numbers.Number
        :param quantity:
          Quantity that the given price is for.  Unit price is
          calculated by ``discounted_unit_price = price / quantity``.
          Note: Quantity could be non-integral (i.e. decimal).
        :type expires_on: numbers.Number|None
        :param expires_on:
          Timestamp, comparable to values returned by :func:`time.time`,
          determining the point in time when the prices are no longer
          valid, or None if no expire time is set (which could mean
          indefinitely, but in reality, it just means undefined).
        """
        assert isinstance(price, Price)
        assert isinstance(base_price, Price)
        assert price.unit_matches_with(base_price)
        assert isinstance(quantity, numbers.Number)
        assert expires_on is None or isinstance(expires_on, numbers.Number)
        assert discounted_unit_price is None or (
            quantity == 0 and
            isinstance(discounted_unit_price, Price) and
            discounted_unit_price.unit_matches_with(price))
        assert base_unit_price is None or (
            quantity == 0 and
            isinstance(base_unit_price, Price) and
            base_unit_price.unit_matches_with(price))

        self.price = price
        self.base_price = base_price
        self.quantity = quantity
        self.expires_on = expires_on
        self._discounted_unit_price = discounted_unit_price
        self._base_unit_price = base_unit_price

    @property
    def discounted_unit_price(self):
        if self._discounted_unit_price is not None:
            return self._discounted_unit_price
        return super(PriceInfo, self).discounted_unit_price

    @property
    def base_unit_price(self):
        if self._base_unit_price is not None:
            return self._base_unit_price
        return super(PriceInfo, self).base_unit_price

    def __repr__(self):
        expire_str = '' if self.expires_on is None else(
            ', expires_on=%r' % (self.expires_on,))
        return "%s(%r, %r, %r%s)" % (
            type(self).__name__, self.price, self.base_price, self.quantity,
            expire_str)
