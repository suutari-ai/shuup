import django_jinja.library
import jinja2
from django.utils.translation import ugettext as _

from shoop.core.pricing import PriceDisplayOptions, Priceful
from shoop.core.utils.prices import convert_taxness


from .shoop_common import money, percent


class _Filter(object):
    def __init__(self, name, property_name=None):
        self.name = name
        self.property_name = (property_name or name)
        self._register()

    def _register(self):
        django_jinja.library.filter(
            name=self.name,
            fn=jinja2.contextfilter(self))


class _PriceDisplayFilter(_Filter):
    def __call__(self, context, item, quantity=1):
        request = context.get('request')
        options = _get_price_display_options(context)
        orig_priceful = _get_priceful(request, item, quantity)
        priceful = _convert_priceful(request, options, item, orig_priceful)
        print(orig_priceful)
        print(priceful)
        price_value = getattr(priceful, self.property_name)
        return _format_price(price_value)


class _PropertyFilter(_Filter):
    def __call__(self, context, item, quantity=1):
        priceful = _get_priceful(context.get('request'), item, quantity)
        return getattr(priceful, self.property_name)


class _PercentPropertyFilter(_Filter):
    def __call__(self, context, item, quantity=1):
        priceful = _get_priceful(context.get('request'), item, quantity)
        return percent(getattr(priceful, self.property_name))


class _TotalPriceDisplayFilter(_Filter):
    def __call__(self, context, source):
        """
        :type source: shoop.core.order_creator.OrderSource|
                      shoop.core.models.Order
        """
        options = _get_price_display_options(context)
        try:
            if options.include_taxes is None:
                total = source.total_price
            elif options.include_taxes:
                total = source.taxful_total_price
            else:
                total = source.taxless_total_price
        except TypeError:
            total = source.total_price
        return _format_price(total)


class _RangePriceDisplayFilter(_Filter):
    def __call__(self, context, product, quantity=1):
        """
        :type product: shoop.core.models.Product
        """
        request = context.get('request')
        options = _get_price_display_options(context)
        priced_children = product.get_priced_children(request, quantity)
        if priced_children:
            (min_product, min_pi) = priced_children[0]
            (max_product, max_pi) = priced_children[-1]
        else:
            min_product = product
            min_pi = _get_priceful(request, product, quantity)
            (max_product, max_pi) = (min_product, min_pi)
        min_pf = _convert_priceful(request, options, min_product, min_pi)
        max_pf = _convert_priceful(request, options, max_product, max_pi)
        return (_format_price(min_pf.price), _format_price(max_pf.price))


def _get_price_display_options(context):
    """
    :type context: jinja2.runtime.Context
    """
    price_display_options = context.get('price_display_options')

    if price_display_options is None:
        request = context.get('request')  # type: django.http.HttpRequest
        price_display_options = getattr(request, 'price_display_options', None)

    if price_display_options is None:
        price_display_options = PriceDisplayOptions()

    return price_display_options


def _get_priceful(request, item, quantity):
    """
    Get priceful from given item.

    If item has `get_price_info` method, it will be called with given
    `request` and `quantity` as arguments, otherwise the item itself
    should implement the `Priceful` interface.

    :type request: django.http.HttpRequest
    :type item: shoop.core.taxing.TaxableItem
    :type quantity: numbers.Number
    :rtype: shoop.core.pricing.Priceful
    """
    if hasattr(item, 'get_price_info'):
        return item.get_price_info(request, quantity=quantity)
    assert isinstance(item, Priceful)
    return item


def _convert_priceful(request, price_display_options, item, priceful):
    """
    Get taxful or taxless price of given item.

    :type request: django.http.HttpRequest
    :type price_display_options: PriceDisplayOptions
    :type item: shoop.core.taxing.TaxableItem
    :type priceful: shoop.core.pricing.Priceful
    :rtype: shoop.core.pricing.Priceful
    """
    wants_taxes = price_display_options.include_taxes
    if wants_taxes is None:
        return priceful
    else:
        return convert_taxness(request, item, priceful, wants_taxes)


def _format_price(price):
    return money(price)
    template = (
        _("{price} (incl. tax)") if price.includes_tax else
        _("E {price} (excl. tax)"))
    return template.format(price=money(price))
