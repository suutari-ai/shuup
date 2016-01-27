from decimal import Decimal

import pytest
from django.utils.encoding import force_text

from shoop.campaigns.models.basket_conditions import (
    BasketTotalAmountCondition, BasketTotalProductAmountCondition,
    ProductsInBasketCondition
)
from shoop.front.basket import get_basket
from shoop.testing.factories import create_product, get_default_supplier
from shoop_tests.campaigns import initialize_test


@pytest.mark.django_db
def test_product_in_basket_condition(rf):
    request, shop, group = initialize_test(rf, False)
    price = shop.create_price

    basket = get_basket(request)
    supplier = get_default_supplier()

    product = create_product("Just-A-Product-Too", shop, default_price="200")
    basket.add_product(supplier=supplier, shop=shop, product=product, quantity=1)

    condition = ProductsInBasketCondition.objects.create()
    condition.values = [product]
    condition.save()

    assert condition.values.first() == product

    assert condition.matches(basket, [])


@pytest.mark.django_db
def test_basket_total_amount_condition(rf):
    request, shop, group = initialize_test(rf, False)
    price = shop.create_price

    basket = get_basket(request)
    supplier = get_default_supplier()

    product = create_product("Just-A-Product-Too", shop, default_price="200")
    basket.add_product(supplier=supplier, shop=shop, product=product, quantity=1)

    condition = BasketTotalAmountCondition.objects.create()
    condition.value = 1
    condition.save()
    assert condition.value == 1
    assert condition.matches(basket, [])


@pytest.mark.django_db
def test_basket_total_value_condition(rf):
    request, shop, group = initialize_test(rf, False)
    price = shop.create_price

    basket = get_basket(request)
    supplier = get_default_supplier()

    product = create_product("Just-A-Product-Too", shop, default_price="200")
    basket.add_product(supplier=supplier, shop=shop, product=product, quantity=1)

    condition = BasketTotalProductAmountCondition.objects.create()
    condition.value = 1
    condition.save()
    assert condition.value == 1
    assert condition.matches(basket, [])
    assert condition.name.lower() in force_text(condition.description)
