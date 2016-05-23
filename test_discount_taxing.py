import base64
import pickle
import zlib
from pprint import pprint

import shoop.core.taxing

ENCODED_ORDER_SOURCE = """
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
CeycPokHWht+wdUr9x+K9gWB
"""


def get_order_source():
    """
    Get order source.

    :rtype: shoop.core.order_creator.OrderSource
    """
    data = zlib.decompress(base64.b64decode(ENCODED_ORDER_SOURCE))
    return pickle.loads(data)


def test_discount_taxing():
    source = get_order_source()

    module = shoop.core.taxing.get_tax_module()
    lines = source.get_final_lines(with_taxes=False)
    print()
    pprint(lines)
    print()

    print('calcing taxes ----------------')
    module.add_taxes(source, lines)
    print('-------------------------------')

    print()
    pprint(lines)
    print()

    print('    Price    Qty Unit price Taxless   Tax%    Taxful    Text')
    for line in lines:
        print('%1s %10.4f %2d %10.4f %10.4f %6.3f %10.4f %s' % (
            line.tax_class.pk if line.tax_class else '',
            line.price,
            line.quantity,
            line.discounted_unit_price,
            line.taxless_price,
            line.tax_percentage,
            line.taxful_price,
            line.text,
        ))

        for line_tax in line.taxes:
            assert isinstance(line_tax, shoop.core.taxing.LineTax)
            print(60 * ' ' + 'Tax %d / %10s: tax=%10.4f base=%10.4f  (%6.3f)' % (
                line_tax.tax.pk,
                line_tax.name,
                line_tax.amount,
                line_tax.base_amount,
                line_tax.rate * 100 if line_tax.rate else 0,
            ))


def main():
    from django.utils import translation
    translation.activate('en')
    test_discount_taxing()
