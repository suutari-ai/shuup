# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
import abc
from collections import defaultdict

import six
from django.conf import settings

from shoop.apps.provides import load_module
from shoop.core.pricing import TaxlessPrice

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
            from ._taxable import TaxableItem

            class Item(TaxableItem):
                tax_class = None
                def __init__(self, tax_class):
                    self.tax_class = tax_class

            import pprint
            pprint.pprint(tax_distribution)
            print(sum(dict(tax_distribution).values()))


            for idx in lines_without_tax_class:
                line = lines[idx]
                taxes = []
                for (tax_class, factor) in tax_distribution:
                    taxed_price = self.get_taxed_price_for(context, Item(tax_class), line.price * factor)
                    taxes.extend(taxed_price.taxes)
                print(taxes)
                line.taxes = taxes

    def _get_line_taxes(self, context, line):
        """
        Get taxes for given source line of an order source.

        :type context: TaxingContext
        :type line: shoop.core.order_creator.SourceLine
        :rtype: Iterable[LineTax]
        """
        taxed_price = self.get_taxed_price_for(context, line, line.price)
        return taxed_price.taxes

    @abc.abstractmethod
    def get_taxed_price_for(self, context, item, price):
        """
        Get TaxedPrice for taxable item.

        Taxable items could be products (`~shoop.core.models.Product`),
        shipping and payment methods (`~shoop.core.models.Method`), and
        lines (`~shoop.core.order_creator.SourceLine`).

        :param context: Taxing context to calculate in
        :type context: TaxingContext
        :param item: Item to get taxes for
        :type item: shoop.core.taxing.TaxableItem
        :param price: Price (taxful or taxless) to calculate taxes for
        :type price: shoop.core.pricing.Price

        :rtype: shoop.core.taxing.TaxedPrice
        """
        pass


def _generate_tax_distribution(lines):
    if not lines:
        return []

    taxless_zero = TaxlessPrice(lines[0].price.new(0).amount)

    total_by_tax_class = defaultdict(lambda: taxless_zero)
    total = taxless_zero

    for (price, tax_class) in _get_taxless_prices_and_tax_classes(lines):
        total_by_tax_class[tax_class] += price
        total += price

    return [
        (tax_class, tax_class_total / total)
        for (tax_class, tax_class_total) in total_by_tax_class.items()
    ]


def _get_taxless_prices_and_tax_classes(lines):
    for line in lines:
        if line.price.includes_tax:
            zero = line.price.new(0).amount
            tax_amount = sum((x.amount for x in line.taxes), zero)
            taxless_price = TaxlessPrice(line.price.amount - tax_amount)
        else:
            taxless_price = line.price
        yield (taxless_price, line.tax_class)
