# This file is part of Shoop.
#
# Copyright (c) 2012-2015, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
from django.conf import settings

from . import numbers


class Money(numbers.UnitedDecimal):
    """
    Money with value and currency.

    The pure decimal value is available from the base classes
    `~shoop.utils.numbers.UnitedDecimal.value` property.

    Money objects with different currencies cannot be compared or
    calculated with and will raise `~shoop.utils.numbers.UnitMixupError`.

    See `__new__`.
    """
    def __new__(cls, value="0", currency=None, *args, **kwargs):
        """
        Create new Money instance with given value and currency.

        If no currency is given explicitly and `value` has a property
        named `currency`, then that will be used.  Otherwise currency is
        a required argument and not passing one will raise a TypeError.

        :param str|numbers.Number value:
          Value as string or number
        :param str|None currency:
          Currency as ISO-4217 code (3-letter string) or None.
        """
        if currency is None and hasattr(value, 'currency'):
            currency = value.currency
        if not currency:
            import pdb
            pdb.set_trace()
            raise TypeError('%s: currency must be given' % cls.__name__)
        instance = super(Money, cls).__new__(cls, value, *args, **kwargs)
        instance._currency = currency
        return instance

    @property
    def currency(self):
        """
        Currency of this money.

        If this `Money` was created with None currency, will return
        `settings.SHOOP_HOME_CURRENCY`.

        :return: Currency as ISO-4217 code (3-letter string)
        :rtype: str
        """
        return (self._currency or settings.SHOOP_HOME_CURRENCY)

    def __repr__(self):
        cls_name = type(self).__name__
        if self._currency is None:
            return "%s('%s')" % (cls_name, self.value)
        return "%s('%s', %r)" % (cls_name, self.value, self._currency)

    def __str__(self):
        return "%s %s" % (self.value, self.currency)

    @classmethod
    def from_data(cls, value, currency):
        return cls(value, currency)

    def unit_matches_with(self, other):
        return (
            (isinstance(other, Money) and self._currency == other._currency)
            or
            (hasattr(other, "currency") and self.currency == other.currency)
        )

    def new(self, value):
        return type(self)(value, currency=self._currency)
