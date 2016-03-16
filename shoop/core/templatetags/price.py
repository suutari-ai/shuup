"""
Template tags for price related operations.
"""

from ._price_filter_impl import (
    _PercentPropertyFilter, _PriceDisplayFilter, _PropertyFilter,
    _RangePriceDisplayFilter, _TotalPriceDisplayFilter
)

# For Product, SourceLine, BasketLine, OrderLine
price = _PriceDisplayFilter('price')
base_price = _PriceDisplayFilter('base_price')
base_unit_price = _PriceDisplayFilter('base_unit_price')
discount_amount = _PriceDisplayFilter('discount_amount')
discounted_unit_price = _PriceDisplayFilter('discounted_unit_price')
unit_discount_amount = _PriceDisplayFilter('unit_discount_amount')
is_discounted = _PropertyFilter('is_discounted')
discount_percent = _PercentPropertyFilter('discount_percent', 'discount_rate')
tax_percent = _PercentPropertyFilter('tax_percent', 'tax_rate')

# For Product
price_range = _RangePriceDisplayFilter('price_range')

# For OrderSource, BaseBasket, Order
total_price = _TotalPriceDisplayFilter('total_price')
