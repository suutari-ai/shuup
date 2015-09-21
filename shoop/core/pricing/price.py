# This file is part of Shoop.
#
# Copyright (c) 2012-2015, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
from shoop.utils.money import Money


class Price(Money):
    """
    Money value with taxful/taxless info.

    Taxful and taxless prices cannot be mixed in comparison or in
    calculations, i.e. operations like ``x < y`` or ``x + y`` for two
    Prices ``x`` and ``y`` with ``x.includes_tax != y.includes_tax``
    will raise an :obj:`~shoop.utils.numbers.UnitMixupError`.

    In addition to `includes_tax` info, Prices are Money and know their
    `~shoop.utils.numbers.UnitedDecimal.value` and
    `~shoop.utils.money.Money.currency`.
    """
    includes_tax = None

    def __new__(cls, value="0", *args, **kwargs):
        if cls == Price:
            raise TypeError('Do not create direct instances of Price')
        return super(Price, cls).__new__(cls, value, *args, **kwargs)

    def unit_matches_with(self, other):
        if not super(Price, self).unit_matches_with(other):
            return False
        self_includes_tax = getattr(self, 'includes_tax', None)
        other_includes_tax = getattr(other, 'includes_tax', None)
        return (self_includes_tax == other_includes_tax)

    @property
    def amount(self):
        """
        Money amount of this price.

        :rtype: Money
        """
        return Money(self.value, self.currency)

    @classmethod
    def from_data(cls, value, currency, includes_tax=None):
        if includes_tax is None:
            if cls.includes_tax is None:
                msg = 'Missing includes_tax argument for %s.from_data'
                raise TypeError(msg % (cls.__name__,))
            includes_tax = cls.includes_tax
        if includes_tax:
            return TaxfulPrice(value, currency)
        else:
            return TaxlessPrice(value, currency)


class TaxfulPrice(Price):
    """
    Price which includes taxes.

    Check the base class, :obj:`Price`,  for more info.
    """
    includes_tax = True


class TaxlessPrice(Price):
    """
    Price which does not include taxes.

    Check the base class, :obj:`Price`,  for more info.
    """
    includes_tax = False
