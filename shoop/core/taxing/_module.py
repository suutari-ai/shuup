# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
import abc
from collections import defaultdict
from itertools import chain

import six
from django.conf import settings

from shoop.apps.provides import load_module

from ._context import TaxingContext


def get_tax_module():
    """
    Get the TaxModule specified in settings.

    :rtype: shoop.core.taxing.TaxModule
    """
    return load_module("SHOOP_TAX_MODULE", "tax_module")()


def should_calculate_taxes_automatically():
    """
    If ``settings.SHOOP_CALCULATE_TAXES_AUTOMATICALLY_IF_POSSIBLE``
    is False taxes shouldn't be calculated automatically otherwise
    use current tax module value ``TaxModule.calculating_is_cheap``
    to determine whether taxes should be calculated automatically.

    :rtype: bool
    """
    if not settings.SHOOP_CALCULATE_TAXES_AUTOMATICALLY_IF_POSSIBLE:
        return False
    return get_tax_module().calculating_is_cheap


class TaxModule(six.with_metaclass(abc.ABCMeta)):
    """
    Module for calculating taxes.
    """
    identifier = None
    name = None

    calculating_is_cheap = True
    taxing_context_class = TaxingContext

    def get_context_from_request(self, request):
        customer = getattr(request, "customer", None)
        return self.get_context_from_data(customer=customer)

    def get_context_from_data(self, **context_data):
        customer = context_data.get("customer")
        customer_tax_group = (
            context_data.get("customer_tax_group") or
            (customer.tax_group if customer else None))
        customer_tax_number = (
            context_data.get("customer_tax_number") or
            getattr(customer, "tax_number", None))
        location = (
            context_data.get("location") or
            context_data.get("shipping_address") or
            (customer.default_shipping_address if customer else None))
        return self.taxing_context_class(
            customer_tax_group=customer_tax_group,
            customer_tax_number=customer_tax_number,
            location=location,
        )

    def get_context_from_order_source(self, source):
        return self.get_context_from_data(
            customer=source.customer, location=source.shipping_address)

    def add_taxes(self, source, lines):
        """
        Add taxes to given OrderSource lines.

        Given lines are modified in-place, also new lines may be added
        (with ``lines.extend`` for example).  If there is any existing
        taxes for the `lines`, they are simply replaced.

        :type source: shoop.core.order_creator.OrderSource
        :param source: OrderSource of the lines
        :type lines: list[shoop.core.order_creator.SourceLine]
        :param lines: List of lines to add taxes for
        """
        context = self.get_context_from_order_source(source)
        lines_without_tax_class = []
        taxed_lines = []
        for (idx, line) in enumerate(lines):
            assert line.source == source
            if not line.parent_line_id:
                if line.tax_class is None:
                    lines_without_tax_class.append(idx)
                else:
                    line.taxes = self._get_line_taxes(context, line)
                    taxed_lines.append(line)

        tax_distribution = _generate_tax_distribution(taxed_lines)

        if tax_distribution:
            import pprint
            pprint.pprint(tax_distribution)
            print(sum(dict(tax_distribution).values()))

            def get_taxes(price, tax_class):
                return self.get_taxed_price(context, price, tax_class).taxes

            for idx in lines_without_tax_class:
                line = lines[idx]

                line.taxes = list(chain.from_iterable(
                    get_taxes(line.price * factor, tax_class)
                    for (tax_class, factor) in tax_distribution))

    def _get_line_taxes(self, context, line):
        """
        Get taxes for given source line of an order source.

        :type context: TaxingContext
        :type line: shoop.core.order_creator.SourceLine
        :rtype: Iterable[LineTax]
        """
        taxed_price = self.get_taxed_price_for(context, line, line.price)
        return taxed_price.taxes

    def get_taxed_price_for(self, context, item, price):
        """
        Get TaxedPrice for taxable item.

        Taxable items could be products (`~shoop.core.models.Product`),
        services (`~shoop.core.models.Service`), or lines
        (`~shoop.core.order_creator.SourceLine`).

        :param context: Taxing context to calculate in
        :type context: TaxingContext
        :param item: Item to get taxes for
        :type item: shoop.core.taxing.TaxableItem
        :param price: Price (taxful or taxless) to calculate taxes for
        :type price: shoop.core.pricing.Price

        :rtype: shoop.core.taxing.TaxedPrice
        """
        return self.get_taxed_price(context, price, item.tax_class)

    @abc.abstractmethod
    def get_taxed_price(self, context, price, tax_class):
        """
        Get TaxedPrice for price and tax class.

        :param context: Taxing context to calculate in
        :type context: TaxingContext
        :param price: Price (taxful or taxless) to calculate taxes for
        :type price: shoop.core.pricing.Price
        :param tax_class: Tax class of the item to get taxes for
        :type tax_class: shoop.core.models.TaxClass

        :rtype: shoop.core.taxing.TaxedPrice
        """
        pass


def _generate_tax_distribution(lines):
    """
    Generate tax distribution from taxed lines.

    :type lines: list[shoop.core.order_creator.SourceLine]
    :param lines: List of lines to generate tax distribution for

    :rtype: list[(shoop.core.models.TaxClass, decimal.Decimal)]
    """
    if not lines:
        return []

    zero = lines[0].price.new(0)

    total_by_tax_class = defaultdict(lambda: zero)
    total = zero

    for line in lines:
        total_by_tax_class[line.tax_class] += line.price
        total += line.price

    if not total:
        # Can't calculate proportions, if total is zero
        return []

    return [
        (tax_class, tax_class_total / total)
        for (tax_class, tax_class_total) in total_by_tax_class.items()
    ]
