from decimal import Decimal

import pytest

from shoop.campaigns.models.basket_conditions import (
    BasketTotalAmountCondition, BasketTotalProductAmountCondition
)
from shoop.campaigns.models.campaigns import BasketCampaign, Coupon
from shoop.core.models import OrderLineType, ShippingMethod
from shoop.front.basket import get_basket
from shoop.front.basket.commands import handle_add_campaign_code
from shoop.testing.factories import (
    create_product, get_default_supplier, get_default_tax_class
)
from shoop_tests.campaigns import initialize_test
from shoop_tests.utils import printable_gibberish


"""
These tests provides proof for following requirements:
case 1: Define if this discount is available only if customer has X amount of products in their basket
case 2: Define if this discount is available if customer has products in their basket for certain amount of money (shipping excluded)
"""

@pytest.mark.django_db
def test_basket_campaign_module_case1(rf):
    request, shop, group = initialize_test(rf, False)
    price = shop.create_price

    basket = get_basket(request)
    supplier = get_default_supplier()

    single_product_price = "50"
    discount_amount_value = "10"

     # create basket rule that requires 2 products in basket
    basket_rule1 = BasketTotalProductAmountCondition.objects.create(value="2")

    product = create_product(printable_gibberish(), shop=shop, supplier=supplier, default_price=single_product_price)

    line = basket.add_product(supplier=supplier, shop=shop, product=product, quantity=1)
    basket.save()

    assert basket.product_count == 1

    campaign = BasketCampaign.objects.create(shop=shop, public_name="test", name="test", discount_amount_value=discount_amount_value, active=True)
    campaign.conditions.add(basket_rule1)
    campaign.save()

    assert len(basket.get_final_lines()) == 1  # case 1
    assert basket.total_price == price(single_product_price) # case 1

    basket.add_product(supplier=supplier, shop=shop, product=product, quantity=1)
    basket.save()

    assert len(basket.get_final_lines()) == 2  # case 1
    assert basket.product_count == 2
    assert basket.total_price == (price(single_product_price) * basket.product_count - price(discount_amount_value))
    assert OrderLineType.DISCOUNT in [l.type for l in basket.get_final_lines()]


@pytest.mark.django_db
def test_basket_campaign_case2(rf):

    request, shop, group = initialize_test(rf, False)
    price = shop.create_price

    basket = get_basket(request)
    supplier = get_default_supplier()
     # create a basket rule that requires atleast value of 200
    rule = BasketTotalAmountCondition.objects.create(value="200")

    single_product_price = "50"
    discount_amount_value = "10"

    unique_shipping_method = ShippingMethod(tax_class=get_default_tax_class(), module_data={"price": 50})
    unique_shipping_method.save()

    for x in range(3):
        product = create_product(printable_gibberish(), shop=shop, supplier=supplier, default_price=single_product_price)
        basket.add_product(supplier=supplier, shop=shop, product=product, quantity=1)

    assert basket.product_count == 3

    campaign = BasketCampaign.objects.create(shop=shop, public_name="test", name="test", discount_amount_value=discount_amount_value, active=True)
    campaign.conditions.add(rule)
    campaign.save()

    assert len(basket.get_final_lines()) == 3
    assert basket.total_price == price(single_product_price) * basket.product_count

    # check that shipping method affects campaign
    basket.shipping_method = unique_shipping_method
    basket.save()
    basket.uncache()
    assert len(basket.get_final_lines()) == 4  # Shipping should not affect the rule being triggered

    line_types = [l.type for l in basket.get_final_lines()]
    assert OrderLineType.DISCOUNT not in line_types

    product = create_product(printable_gibberish(), shop=shop, supplier=supplier, default_price=single_product_price)
    basket.add_product(supplier=supplier, shop=shop, product=product, quantity=1)

    assert len(basket.get_final_lines()) == 6  # Discount included
    assert OrderLineType.DISCOUNT in [l.type for l in basket.get_final_lines()]


@pytest.mark.django_db
def test_only_cheapest_price_is_selected(rf):
    request, shop, group = initialize_test(rf, False)
    price = shop.create_price

    basket = get_basket(request)
    supplier = get_default_supplier()
     # create a basket rule that requires atleast value of 200
    rule = BasketTotalAmountCondition.objects.create(value="200")

    product_price = "200"

    discount1 = "10"
    discount2 = "20"  # should be selected
    product = create_product(printable_gibberish(), shop=shop, supplier=supplier, default_price=product_price)
    basket.add_product(supplier=supplier, shop=shop, product=product, quantity=1)

    campaign = BasketCampaign.objects.create(shop=shop, public_name="test", name="test", discount_amount_value=discount1, active=True)
    campaign.conditions.add(rule)
    campaign.save()

    campaign = BasketCampaign.objects.create(shop=shop, public_name="test", name="test", discount_amount_value=discount2, active=True)
    campaign.conditions.add(rule)
    campaign.save()

    assert len(basket.get_final_lines()) == 2
    line_types = [l.type for l in basket.get_final_lines()]
    assert OrderLineType.DISCOUNT in line_types

    for line in basket.get_final_lines():
        if line.type == OrderLineType.DISCOUNT:
            assert line.discount_amount == price(discount2)


@pytest.mark.django_db
def test_multiple_campaigns_match_with_coupon(rf):
    request, shop, group = initialize_test(rf, False)
    price = shop.create_price

    basket = get_basket(request)
    supplier = get_default_supplier()
     # create a basket rule that requires atleast value of 200
    rule = BasketTotalAmountCondition.objects.create(value="200")

    product_price = "200"

    discount1 = "10"
    discount2 = "20"
    product = create_product(printable_gibberish(), shop=shop, supplier=supplier, default_price=product_price)
    basket.add_product(supplier=supplier, shop=shop, product=product, quantity=1)

    campaign = BasketCampaign.objects.create(shop=shop, public_name="test", name="test", discount_amount_value=discount1, active=True)
    campaign.conditions.add(rule)
    campaign.save()

    dc = Coupon.objects.create(code="TEST", active=True)
    campaign2 = BasketCampaign.objects.create(
            shop=shop, public_name="test",
            name="test",
            coupon=dc,
            discount_amount_value=discount2,
            active=True
    )

    basket.add_product(supplier=supplier, shop=shop, product=product, quantity=1)

    resp = handle_add_campaign_code(request, basket, dc.code)
    assert resp.get("ok")

    discount_lines_values = [line.discount_amount for line in basket.get_final_lines()]
    assert price(discount1) in discount_lines_values
    assert price(discount2) in discount_lines_values
    assert basket.total_price == (price(product_price) * basket.product_count - price(discount1) - price(discount2))


@pytest.mark.django_db
def test_percentage_campaign(rf):
    request, shop, group = initialize_test(rf, False)
    price = shop.create_price

    basket = get_basket(request)
    supplier = get_default_supplier()
     # create a basket rule that requires atleast value of 200
    rule = BasketTotalAmountCondition.objects.create(value="200")

    product_price = "200"

    discount_percentage = "0.1"

    expected_discounted_price = price(product_price) - (price(product_price) * Decimal(discount_percentage))

    product = create_product(printable_gibberish(), shop=shop, supplier=supplier, default_price=product_price)
    basket.add_product(supplier=supplier, shop=shop, product=product, quantity=1)

    campaign = BasketCampaign.objects.create(shop=shop, public_name="test", name="test", discount_percentage=discount_percentage, active=True)
    campaign.conditions.add(rule)
    campaign.save()


    assert len(basket.get_final_lines()) == 2
    assert basket.product_count == 1
    assert basket.total_price == expected_discounted_price
