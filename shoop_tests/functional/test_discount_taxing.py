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
    create_product, get_payment_method, get_shipping_method, get_shop
)


def setup_module(module):
    global settings_overrider
    settings_overrider = override_settings(
        SHOOP_CALCULATE_TAXES_AUTOMATICALLY_IF_POSSIBLE=False)
    settings_overrider.__enter__()


def teardown_module(module):
    settings_overrider.__exit__(None, None, None)


@pytest.mark.django_db
@pytest.mark.parametrize("taxes", ['taxful', 'taxless'])
def test_discount_taxing_1prod(taxes):
    source = create_order_source(
        prices_include_tax=(taxes == 'taxful'),
        line_data=[
            'product: P1      |price: 200.00|qty: 1|discount:  0.00|tax: A',
            'discount: SALE   |price: -20.00|qty: 1|discount: 20.00',
        ],
        tax_rates={'A': '0.25'})
    source.calculate_taxes()

    assert source.total_price.value == 180
    assert get_price_by_tax_class(source) == {'TC-A': 200, '': -20}

    if taxes == 'taxful':
        #    Name  Rate    Base amount     Tax amount         Taxful
        assert get_pretty_tax_summary(source) == [
            'Tax-A 0.25  144.000000000   36.000000000  180.000000000']
        assert get_pretty_line_taxes_of_discount_lines(source) == [[
            'Tax-A 0.25  -16.000000000   -4.000000000  -20.000000000']]
    else:
        assert get_pretty_tax_summary(source) == [
            'Tax-A 0.25  180.000000000   45.000000000  225.000000000']
        assert get_pretty_line_taxes_of_discount_lines(source) == [[
            'Tax-A 0.25  -20.000000000   -5.000000000  -25.000000000']]


@pytest.mark.django_db
@pytest.mark.parametrize("taxes", ['taxful', 'taxless'])
def test_discount_taxing_2prods(taxes):
    source = create_order_source(
        prices_include_tax=(taxes == 'taxful'),
        line_data=[
            'product: P1      |price:  10.00|qty: 1|discount:  0.00|tax: A',
            'product: P2      |price:  20.00|qty: 1|discount:  0.00|tax: B',
            'discount: SALE   |price:  -3.00|qty: 1|discount:  3.00',
        ],
        tax_rates={'A': '0.25', 'B': '0.20'})
    source.calculate_taxes()

    assert source.total_price.value == 27
    assert get_price_by_tax_class(source) == {'TC-A': 10, 'TC-B': 20, '': -3}

    if taxes == 'taxful':
        #    Name  Rate    Base amount     Tax amount         Taxful
        assert get_pretty_tax_summary(source) == [
            'Tax-A 0.25    7.200000000    1.800000000    9.000000000',
            'Tax-B 0.20   15.000000000    3.000000000   18.000000000']
        assert get_pretty_line_taxes_of_discount_lines(source) == [[
            'Tax-A 0.25   -0.800000000   -0.200000000   -1.000000000',
            'Tax-B 0.20   -1.666666667   -0.333333333   -2.000000000']]
    else:
        assert get_pretty_tax_summary(source) == [
            'Tax-A 0.25    9.000000000    2.250000000   11.250000000',
            'Tax-B 0.20   18.000000000    3.600000000   21.600000000']
        assert get_pretty_line_taxes_of_discount_lines(source) == [[
            'Tax-A 0.25   -1.000000000   -0.250000000   -1.250000000',
            'Tax-B 0.20   -2.000000000   -0.400000000   -2.400000000']]


@pytest.mark.django_db
@pytest.mark.parametrize("taxes", ['taxful', 'taxless'])
def test_discount_taxing_3prods_with_services(taxes):
    source = create_order_source(
        prices_include_tax=(taxes == 'taxful'),
        line_data=[
            'product: P1      |price:  10.00|qty: 2|discount:  2.00|tax: A',
            'product: P2      |price:  40.00|qty: 8|discount:  0.00|tax: B',
            'product: P3      |price:  60.00|qty: 6|discount: 12.00|tax: C',
            'payment: Invoice |price:   2.50|qty: 1|discount:  0.00|tax: A',
            'shipping: Ship   |price:   7.50|qty: 1|discount:  0.00|tax: A',
            'discount: SALE   |price: -30.00|qty: 1|discount: 30.00',
        ],
        tax_rates={'A': '0.25', 'B': '0.15', 'C': '0.30'})
    source.calculate_taxes()

    assert source.total_price.value == 90
    assert get_price_by_tax_class(source) == {
        'TC-A': 20, 'TC-B': 40, 'TC-C': 60, '': -30}

    if taxes == 'taxful':
        #    Name  Rate    Base amount     Tax amount         Taxful
        assert get_pretty_tax_summary(source) == [
            'Tax-C 0.30   34.615384615   10.384615385   45.000000000',
            'Tax-A 0.25   12.000000000    3.000000000   15.000000000',
            'Tax-B 0.15   26.086956522    3.913043478   30.000000000',
        ]
        assert get_pretty_line_taxes_of_discount_lines(source) == [[
            'Tax-A 0.25   -4.000000000   -1.000000000   -5.000000000',
            'Tax-B 0.15   -8.695652174   -1.304347826  -10.000000000',
            'Tax-C 0.30  -11.538461538   -3.461538462  -15.000000000',
        ]]
    else:
        assert get_pretty_tax_summary(source) == [
            'Tax-C 0.30   45.000000000   13.500000000   58.500000000',
            'Tax-A 0.25   15.000000000    3.750000000   18.750000000',
            'Tax-B 0.15   30.000000000    4.500000000   34.500000000',
        ]
        assert get_pretty_line_taxes_of_discount_lines(source) == [[
            'Tax-A 0.25   -5.000000000   -1.250000000   -6.250000000',
            'Tax-B 0.15  -10.000000000   -1.500000000  -11.500000000',
            'Tax-C 0.30  -15.000000000   -4.500000000  -19.500000000',
        ]]


@pytest.mark.django_db
@pytest.mark.parametrize("taxes", ['taxful', 'taxless'])
def test_discount_taxing_all_discounted(taxes):
    source = create_order_source(
        prices_include_tax=(taxes == 'taxful'),
        line_data=[
            'product: P1      |price:  10.00|qty: 1|discount:  0.00|tax: A',
            'product: P2      |price:  20.00|qty: 1|discount:  0.00|tax: B',
            'discount: SALE   |price: -30.00|qty: 1|discount: 30.00',
        ],
        tax_rates={'A': '0.20', 'B': '0.10'})
    source.calculate_taxes()

    assert source.total_price.value == 0
    assert get_price_by_tax_class(source) == {'TC-A': 10, 'TC-B': 20, '': -30}

    if taxes == 'taxful':
        #    Name  Rate    Base amount     Tax amount         Taxful
        assert get_pretty_tax_summary(source) == [
            'Tax-A 0.20    0.000000000    0.000000000    0.000000000',
            'Tax-B 0.10    0.000000000    0.000000000    0.000000000',
        ]
        assert get_pretty_line_taxes_of_discount_lines(source) == [[
            'Tax-A 0.20   -8.333333333   -1.666666667  -10.000000000',
            'Tax-B 0.10  -18.181818182   -1.818181818  -20.000000000',
        ]]
    else:
        assert get_pretty_tax_summary(source) == [
            'Tax-A 0.20    0.000000000    0.000000000    0.000000000',
            'Tax-B 0.10    0.000000000    0.000000000    0.000000000',
        ]
        assert get_pretty_line_taxes_of_discount_lines(source) == [[
            'Tax-A 0.20  -10.000000000   -2.000000000  -12.000000000',
            'Tax-B 0.10  -20.000000000   -2.000000000  -22.000000000',
        ]]

# ================================================================
# Test data creating
# ================================================================


class Line(object):
    def __init__(self, price, quantity=1, discount=0, **kwargs):
        self.price = Decimal(price)
        self.quantity = Decimal(quantity)
        self.discount = Decimal(discount)
        self.__dict__.update(kwargs)
        self.base_unit_price = (self.price + self.discount) / self.quantity
        self.is_product = ('product_sku' in kwargs)
        self.is_payment = ('payment_name' in kwargs)
        self.is_shipping = ('shipping_name' in kwargs)
        self.is_discount = ('discount_text' in kwargs)

    @classmethod
    def from_text(cls, text):
        """
            'product: P1      |price:  10.00|qty: 2|disc:  2.00|tax: A',
            'product: P2      |price:  40.00|qty: 8|disc:  0.00|tax: B',
            'product: P3      |price:  60.00|qty: 6|disc: 12.00|tax: C',
            'payment: Invoice |price:   2.50|qty: 1|disc:  0.00|tax: A',
            'shipping: Ship   |price:   7.50|qty: 1|disc:  0.00|tax: A',
            'discount: SALE   |price: -30.00|qty: 1|disc: 30.00',
        """
        preparsed = (item.split(':') for item in text.split('|'))
        data = {x[0].strip(): x[1].strip() for x in preparsed}
        mappings = [
            ('product', 'product_sku'),
            ('payment', 'payment_name'),
            ('shipping', 'shipping_name'),
            ('discount', 'discount_text'),
            ('qty', 'quantity'),
            ('disc', 'discount'),
            ('tax', 'tax_name'),
        ]
        for (old_key, new_key) in mappings:
            if old_key in data:
                data[new_key] = data[old_key]
                del data[old_key]
        return cls(**data)


def create_order_source(prices_include_tax, line_data, tax_rates):
    """
    Get order source with some testing data.

    :rtype: OrderSource
    """
    lines = [Line.from_text(x) for x in line_data]
    shop = get_shop(prices_include_tax, currency='USD')
    tax_classes = create_assigned_tax_classes(tax_rates)
    products = create_products(shop, lines, tax_classes)
    services = create_services(shop, lines, tax_classes)

    source = OrderSource(shop)
    fill_order_source(source, lines, products, services)
    return source


def create_assigned_tax_classes(tax_rates):
    return {
        tax_name: create_assigned_tax_class(tax_name, tax_rate)
        for (tax_name, tax_rate) in tax_rates.items()
    }


def create_assigned_tax_class(name, tax_rate):
    """
    Create a tax class and assign a tax for it with a tax rule.
    """
    tax_class = TaxClass.objects.create(name='TC-%s' % name)
    tax = Tax.objects.create(rate=tax_rate, name='Tax-%s' % name)
    TaxRule.objects.create(tax=tax).tax_classes.add(tax_class)
    return tax_class


def create_products(shop, lines, tax_classes):
    return {
        line.product_sku: create_product(
            line.product_sku, shop,
            default_price=line.base_unit_price,
            tax_class=tax_classes[line.tax_name]
        )
        for line in lines if line.is_product
    }


def create_services(shop, lines, tax_classes):
    def service_name(line):
        return 'payment_method' if line.is_payment else 'shipping_method'
    return {
        service_name(line): create_service(shop, line, tax_classes)
        for line in lines if (line.is_payment or line.is_shipping)
    }


def create_service(shop, line, tax_classes):
    assert line.quantity == 1 and line.discount == 0
    if line.is_payment:
        meth = get_payment_method(
            shop=shop, price=line.price, name=line.payment_name)
    elif line.is_shipping:
        meth = get_shipping_method(
            shop=shop, price=line.price, name=line.shipping_name)
    meth.tax_class = tax_classes[line.tax_name]
    meth.save()
    return meth


def fill_order_source(source, lines, products, services):
    for line in lines:
        if line.is_product:
            source.add_line(
                product=products[line.product_sku],
                quantity=line.quantity,
                base_unit_price=source.create_price(line.base_unit_price),
                discount_amount=source.create_price(line.discount),
            )
        elif line.is_payment:
            source.payment_method = services['payment_method']
        elif line.is_shipping:
            source.shipping_method = services['shipping_method']
        elif line.is_discount:
            source.add_line(
                type=OrderLineType.DISCOUNT,
                quantity=line.quantity,
                base_unit_price=source.create_price(line.base_unit_price),
                discount_amount=source.create_price(line.discount),
                text=line.discount_text,
            )


# ================================================================
# Formatting results
# ================================================================


def get_price_by_tax_class(source):
    price_by_tax_class = defaultdict(Decimal)
    for line in source.get_final_lines(with_taxes=False):
        tax_class_name = (line.tax_class.name if line.tax_class else '')
        price_by_tax_class[tax_class_name] += line.price.value
    return price_by_tax_class


TAX_DISTRIBUTION_LINE_FORMAT = (
    '{n:5s} {r:4.2f} {ba:14.9f} {a:14.9f} {t:14.9f}')


def get_pretty_tax_summary(source):
    summary = get_tax_summary(source)
    return [prettify_tax_summary_line(line) for line in summary]


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


def prettify_tax_summary_line(line):
    """
    Format tax summary line as pretty string.

    :type line: shoop.core.taxing._tax_summary.TaxSummaryLine
    :rtype: str
    """
    return TAX_DISTRIBUTION_LINE_FORMAT.format(
        n=line.tax_name, r=line.tax_rate,
        ba=line.based_on, a=line.tax_amount, t=line.taxful)


def get_pretty_line_taxes_of_discount_lines(source):
    return [
        prettify_line_taxes(line)
        for line in source.get_final_lines()
        if line.tax_class is None]


def prettify_line_taxes(line):
    return [
        prettify_line_tax(line_tax)
        for line_tax in sorted(line.taxes, key=(lambda x: x.name))]


def prettify_line_tax(line_tax):
    """
    Format line tax as pretty string.

    :type line_tax: shoop.core.taxing.LineTax
    :rtype: str
    """
    return TAX_DISTRIBUTION_LINE_FORMAT.format(
        n=line_tax.name, r=line_tax.rate,
        ba=line_tax.base_amount, a=line_tax.amount,
        t=(line_tax.base_amount + line_tax.amount))
