from collections import defaultdict
from decimal import Decimal

from django.test.utils import override_settings
import pytest


from shoop.core.models import OrderLineType, Tax, TaxClass
from shoop.core.order_creator import OrderSource
from shoop.core.pricing import TaxlessPrice
from shoop.core.taxing import TaxSummary
from shoop.default_tax.models import TaxRule


from shoop.testing.factories import (
    create_product, get_default_shop, get_payment_method,
    get_shipping_method,
)


def setup_module(module):
    global settings_overrider
    settings_overrider = override_settings(
        SHOOP_CALCULATE_TAXES_AUTOMATICALLY_IF_POSSIBLE=False)
    settings_overrider.__enter__()


def teardown_module(module):
    settings_overrider.__exit__(None, None, None)


@pytest.mark.django_db
def test_discount_taxing():
    source = get_order_source()
    price = source.create_price
    money = price(0).amount.new

    assert not any(line.taxes for line in source.get_lines()), "No taxes yet"

    assert source.total_price == price(90)
    assert get_price_distribution_by_tax_class(source) == {
        'TC-A': 20, 'TC-B': 40, 'TC-C': 60, None: -30}

    source.calculate_taxes()

    assert all(line.taxes for line in source.get_lines()), "Taxes are known"

    assert source.total_price == price(90)
    assert get_price_distribution_by_tax_class(source) == {
        'TC-A': 20, 'TC-B': 40, 'TC-C': 60, None: -30}

    # Check that discount line taxes are calculated correctly
    discount_line = [
        line for line in source.get_final_lines()
        if line.tax_class is None][0]  # The only one without tax class

    assert len(discount_line.taxes) == 3, "Discount line has taxes"
    taxful_by_tax = {
        line_tax.name: line_tax.base_amount + line_tax.amount
        for line_tax in discount_line.taxes
    }
    # TC-A, TC-B and TC-C have 20 EUR, 40 EUR and 60 EUR, total 120 EUR.
    # Price of the discount line (-30 EUR) should be divided to the tax
    # classes in that proportion:
    assert_almost_equal(taxful_by_tax['Tax-A'], price(-30.0 * 20 / 120))
    assert_almost_equal(taxful_by_tax['Tax-B'], price(-30.0 * 40 / 120))
    assert_almost_equal(taxful_by_tax['Tax-C'], price(-30.0 * 60 / 120))

    line_tax_by_tax = {x.name: x for x in discount_line.taxes}
    ltax1 = line_tax_by_tax['Tax-A']
    ltax2 = line_tax_by_tax['Tax-B']
    ltax3 = line_tax_by_tax['Tax-C']
    assert_almost_equal(ltax1.rate, Decimal('0.25'))
    assert_almost_equal(ltax2.rate, Decimal('0.15'))
    assert_almost_equal(ltax3.rate, Decimal('0.30'))
    assert_almost_equal(ltax1.amount, money('-1.000000000'))
    assert_almost_equal(ltax2.amount, money('-1.304347826'))
    assert_almost_equal(ltax3.amount, money('-3.461538461'))
    assert_almost_equal(ltax1.base_amount, money('-4.000000000'))
    assert_almost_equal(ltax2.base_amount, money('-8.695652173'))
    assert_almost_equal(ltax3.base_amount, money('-11.538461538'))

    tax_summary = get_tax_summary(source)

    summary_line_by_tax_name = {line.tax_name: line for line in tax_summary}
    line1 = summary_line_by_tax_name['Tax-A']
    line2 = summary_line_by_tax_name['Tax-B']
    line3 = summary_line_by_tax_name['Tax-C']

    assert_almost_equal(line1.taxful, money(15))
    assert_almost_equal(line2.taxful, money(30))
    assert_almost_equal(line3.taxful, money(45))

    assert len(tax_summary) == 3, "There is no untaxed prices"


def get_price_distribution_by_tax_class(source):
    price_by_tax_class = defaultdict(Decimal)
    for line in source.get_final_lines(with_taxes=False):
        tax_class_name = (line.tax_class.name if line.tax_class else None)
        price_by_tax_class[tax_class_name] += line.price.value

    return dict(price_by_tax_class)


def get_tax_summary(source):
    """
    Get tax summary of given source lines.

    :type source: OrderSource
    :type lines: list[SourceLine]
    :rtype: TaxSummary
    """
    all_line_taxes = []
    untaxed = TaxlessPrice(source.create_price(0).amount)
    for line in source.get_final_lines():
        line_taxes = list(line.taxes)
        all_line_taxes.extend(line_taxes)
        if not line_taxes:
            untaxed += line.taxless_price
    return TaxSummary.from_line_taxes(all_line_taxes, untaxed)


def get_order_source():
    """
    Get order source with some testing data.

    :rtype: OrderSource
    """
    (shop, prod1, prod2, prod3) = create_base_objects()
    source = create_order_source(
        shop,
        [
            {'product': prod1, 'quantity': 2, 'total_discount': 2},
            {'product': prod2, 'quantity': 8, 'total_discount': 0},
            {'product': prod3, 'quantity': 6, 'total_discount': 12},
        ],
        {'name': 'Invoice', 'price': '2.5', 'tax_class': prod1.tax_class},
        {'name': 'Ship to home', 'price': '7.5', 'tax_class': prod1.tax_class},
    )
    source.add_line(
        type=OrderLineType.DISCOUNT,
        quantity=1,
        base_unit_price=source.create_price(0),
        discount_amount=source.create_price(30),
        text='Buy much, get much',
    )
    return source


def create_base_objects():
    shop = get_default_shop()
    assert shop.prices_include_tax is True
    assert shop.currency == 'EUR'
    tc1 = create_assigned_tax_class('A', '0.25')
    tc2 = create_assigned_tax_class('B', '0.15')
    tc3 = create_assigned_tax_class('C', '0.30')
    prod1 = create_product('P1', shop, default_price=6, tax_class=tc1)
    prod2 = create_product('P2', shop, default_price=5, tax_class=tc2)
    prod3 = create_product('P3', shop, default_price=12, tax_class=tc3)
    return (shop, prod1, prod2, prod3)


def create_assigned_tax_class(name, tax_rate):
    tax_class = TaxClass.objects.create(name='TC-%s' % name)
    tax = Tax.objects.create(rate=tax_rate, name='Tax-%s' % name)
    TaxRule.objects.create(tax=tax).tax_classes.add(tax_class)
    return tax_class


def create_order_source(shop, line_data, payment, shipping):
    source = OrderSource(shop)
    for record in line_data:
        prod = record['product']
        source.add_line(
            product=prod,
            quantity=record['quantity'],
            base_unit_price=prod.get_shop_instance(shop).default_price,
            discount_amount=source.create_price(record['total_discount']))
    source.payment_method = create_payment_method(
        price=payment['price'], tax_class=payment['tax_class'])
    source.shipping_method = create_shipping_method(
        price=shipping['price'], tax_class=shipping['tax_class'])
    return source


def create_payment_method(price, tax_class):
    pm = get_payment_method(price=price, name='Invoice')
    pm.tax_class = tax_class
    pm.save()
    return pm


def create_shipping_method(price, tax_class):
    sm = get_shipping_method(price=price, name='Ship to home')
    sm.tax_class = tax_class
    sm.save()
    return sm

def assert_almost_equal(x, y):
    if hasattr(x, 'unit_matches_with'):
        assert x.unit_matches_with(y)
    assert Decimal(abs(x - y)) < 0.0000001
