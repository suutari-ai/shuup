# This file is part of Shoop.
#
# Copyright (c) 2012-2015, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
import abc

from django.http import HttpRequest
import six

from shoop.apps.provides import load_module
from shoop.core.pricing import TaxfulPrice, TaxlessPrice

from ._context import TaxingContext
from ._price import TaxedPrice


def get_tax_module():
    """
    Get the TaxModule specified in settings.

    :rtype: shoop.core.taxing.TaxModule
    """
    return load_module("SHOOP_TAX_MODULE", "tax_module")()


class TaxModule(six.with_metaclass(abc.ABCMeta)):
    """
    Module for calculating taxes.
    """
    identifier = None
    name = None

    taxing_context_class = TaxingContext

    def get_context(self, context):
        """
        :rtype: TaxingContext
        """
        if isinstance(context, self.taxing_context_class):
            return context
        elif isinstance(context, HttpRequest):
            return self.get_context_from_request(context)
        else:
            return self.get_context_from_data(**(context or {}))

    def get_context_from_request(self, request):
        # This implementation does not use `request` at all.
        return self.taxing_context_class()

    def get_context_from_data(self, **context_data):
        return self.taxing_context_class(**context_data)

    # TODO: (TAX) Remove get_method_tax_amount? (Not needed probably)
    # def get_method_tax_amount(self, tax_view, method):
    #     pass

    @abc.abstractmethod
    def add_taxes(self, source, lines):
        """
        Add taxes to given OrderSource lines.

        Given lines are modified in-place, also new lines may be added
        (with ``lines.extend`` for example).

        :type source: shoop.core.order_creator.OrderSource
        :type lines: list[shoop.core.order_creator.SourceLine]
            """
        pass
