# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
import pytest

from django.utils.encoding import force_text

from shoop.campaigns.models.cart_conditions import (
    CartTotalAmountCondition, CartTotalProductAmountCondition,
    ProductsInCartCondition
)
from shoop.front.cart import get_cart
from shoop.testing.factories import get_default_supplier, create_product
from shoop_tests.campaigns import initialize_test


@pytest.mark.django_db
def test_product_in_cart_condition(rf):
    request, shop, group = initialize_test(rf, False)

    cart = get_cart(request)
    supplier = get_default_supplier()

    product = create_product("Just-A-Product-Too", shop, default_price="200")
    cart.add_product(supplier=supplier, shop=shop, product=product, quantity=1)

    condition = ProductsInCartCondition.objects.create()
    condition.values = [product]
    condition.save()

    assert condition.values.first() == product

    assert condition.matches(cart, [])


@pytest.mark.django_db
def test_cart_total_amount_condition(rf):
    request, shop, group = initialize_test(rf, False)

    cart = get_cart(request)
    supplier = get_default_supplier()

    product = create_product("Just-A-Product-Too", shop, default_price="200")
    cart.add_product(supplier=supplier, shop=shop, product=product, quantity=1)

    condition = CartTotalAmountCondition.objects.create()
    condition.value = 1
    condition.save()
    assert condition.value == 1
    assert condition.matches(cart, [])


@pytest.mark.django_db
def test_cart_total_value_condition(rf):
    request, shop, group = initialize_test(rf, False)

    cart = get_cart(request)
    supplier = get_default_supplier()

    product = create_product("Just-A-Product-Too", shop, default_price="200")
    cart.add_product(supplier=supplier, shop=shop, product=product, quantity=1)

    condition = CartTotalProductAmountCondition.objects.create()
    condition.value = 1
    condition.save()
    assert condition.value == 1
    assert condition.matches(cart, [])
    assert "cart has at least the product count entered here" in force_text(condition.description)
