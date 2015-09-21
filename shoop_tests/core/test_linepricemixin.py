# -*- coding: utf-8 -*-
# This file is part of Shoop.
#
# Copyright (c) 2012-2015, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.

from decimal import Decimal

from shoop.core.pricing import TaxfulPrice, TaxlessPrice
from shoop.core.utils.prices import LinePriceMixin
from shoop.utils.money import Money


def create_line(per_unit, quantity, discount, tax_amount, taxful=True):
    price_cls = TaxfulPrice if taxful else TaxlessPrice

    class TestLine(LinePriceMixin):
        def __init__(self):
            self.unit_price = price_cls(per_unit, 'EUR')
            self.quantity = quantity
            self.total_discount = price_cls(discount, 'EUR')
            self.total_tax_amount = Money(tax_amount, 'EUR')

    return TestLine()


def test_basics():
    line = create_line(5, 9, 12, 3)
    assert line.total_price == TaxfulPrice(33, 'EUR')  # 5 * 9 - 12
    assert line.taxful_total_price == line.total_price
    assert line.taxless_total_price == TaxlessPrice(30, 'EUR')  # 33 - 3
    assert_almost_equal(line.tax_rate, Decimal('0.1'))  # 3 / 30
    assert_almost_equal(line.tax_percentage, 10)
    assert_almost_equal(
        line.taxless_unit_price, TaxlessPrice('4.5', 'EUR'))  # 5 -10 %
    assert_almost_equal(
        line.taxless_total_discount, TaxlessPrice('11.88', 'EUR'))  # 12 -10 %


def assert_almost_equal(x, y):
    assert Decimal(abs(x - y)) < 0.0000000000000000000000001
