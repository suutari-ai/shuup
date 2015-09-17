# This file is part of Shoop.
#
# Copyright (c) 2012-2015, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
from django.conf import settings

from . import numbers


class Money(numbers.UnitedDecimal):
    def __new__(cls, value="0", currency=None, *args, **kwargs):
        instance = super(Money, cls).__new__(cls, value, *args, **kwargs)
        instance._currency = currency
        return instance

    @property
    def currency(self):
        return (self._currency or settings.SHOOP_HOME_CURRENCY)

    def __repr__(self):
        cls_name = type(self).__name__
        if self._currency is None:
            return "%s('%s')" % (cls_name, self.value)
        return "%s('%s', %r)" % (cls_name, self.value, self._currency)

    def __str__(self):
        return "%s %s" % (self.value, self.currency)

    def unit_matches_with(self, other):
        return (
            (isinstance(other, Money) and self._currency == other._currency)
            or
            (hasattr(other, "currency") and self.currency == other.currency)
        )

    def new(self, value):
        return type(self)(value, currency=self._currency)
