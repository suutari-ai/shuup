# This file is part of Shoop.
#
# Copyright (c) 2012-2015, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.

from shoop.core.models import Shop


class CurrencyBound(object):
    def __init__(self, currency=None, *args, **kwargs):
        self._currency = currency
        super(CurrencyBound, self).__init__(*args, **kwargs)

    @property
    def currency(self):
        if self._currency is None:
            first_shop = Shop.objects.first()
            if first_shop:
                self._currency = first_shop.currency
        return self._currency
