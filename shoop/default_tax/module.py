# This file is part of Shoop.
#
# Copyright (c) 2012-2015, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
from django.utils.translation import ugettext_lazy as _

from shoop.core import taxing
from shoop.core.pricing import TaxfulPrice, TaxlessPrice
from shoop.core.taxing._context import TaxingContext
from shoop.core.taxing.utils import stacked_value_added_taxes
from shoop.default_tax.models import TaxRule
from shoop.utils.iterables import first


class DefaultTaxModule(taxing.TaxModule):
    identifier = "default_tax"
    name = _("Default Taxation")

    def add_taxes(self, source, lines):
        super(DefaultTaxModule, self).add_taxes(source, lines)
        tax_group = (source.customer.tax_group if source.customer else None)
        taxing_context = TaxingContext(
            customer_tax_group=tax_group,
            location=source.billing_address,
        )
        for line in lines:
            assert line.source == source
            if not line.parent_line_id:
                line.taxes = self._get_line_taxes(taxing_context, line)

    def _get_line_taxes(self, taxing_context, source_line):
        """
        Get taxes for given source line of an order source.

        :type taxing_context: TaxingContext
        :type source_line: shoop.core.order_creator.SourceLine
        :rtype: Iterable[LineTax]
        """
        return _calculate_taxes(
            source_line.total_price,
            taxing_context=taxing_context,
            tax_class=source_line.get_tax_class(),
        ).taxes


def _calculate_taxes(price, taxing_context, tax_class):
    customer_tax_group = taxing_context.customer_tax_group
    # TODO: (TAX) Should tax exempt be done in some better way?
    if customer_tax_group and customer_tax_group.identifier == 'tax_exempt':
        return taxing.TaxedPrice(
            TaxfulPrice(price.amount), TaxlessPrice(price.amount), [])

    tax_rules = TaxRule.objects.filter(enabled=True, tax_classes=tax_class)
    if customer_tax_group:
        tax_rules = tax_rules.filter(customer_tax_groups=customer_tax_group)
    tax_rules = tax_rules.order_by("-priority")  # TODO: (TAX) Do the Right Thing with priority
    taxes = [tax_rule for tax_rule in tax_rules if tax_rule.matches(taxing_context)]
    tax_rule = first(taxes)  # TODO: (TAX) Do something better than just using the first tax!
    tax = getattr(tax_rule, "tax", None)
    return stacked_value_added_taxes(price, [tax] if tax else [])
