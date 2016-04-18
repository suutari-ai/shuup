# -*- coding: utf-8 -*-
# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
import pytest
from django.db.models import Sum
from django.test.utils import override_settings

from shoop.core.models import ShippingMode
from shoop.front.cart import get_cart
from shoop.front.models import StoredCart
from shoop.testing.factories import (
    create_product, get_default_shop, get_default_payment_method,
    get_default_supplier
)
from shoop.testing.utils import apply_request_middleware
from shoop_tests.utils import printable_gibberish


@pytest.mark.django_db
@pytest.mark.parametrize("storage", [
    "shoop.front.cart.storage:DirectSessionCartStorage",
    "shoop.front.cart.storage:DatabaseCartStorage",
])
def test_cart(rf, storage):
    StoredCart.objects.all().delete()
    quantities = [3, 12, 44, 23, 65]
    shop = get_default_shop()
    get_default_payment_method()  # Can't create carts without payment methods
    supplier = get_default_supplier()
    products_and_quantities = []
    for quantity in quantities:
        product = create_product(printable_gibberish(), shop=shop, supplier=supplier, default_price=50)
        products_and_quantities.append((product, quantity))

    is_database = (storage == "shoop.front.cart.storage:DatabaseCartStorage")
    with override_settings(SHOOP_CART_STORAGE_CLASS_SPEC=storage):
        for product, q in products_and_quantities:
            request = rf.get("/")
            request.session = {}
            request.shop = shop
            apply_request_middleware(request)
            cart = get_cart(request)
            assert cart == request.cart
            assert cart.product_count == 0
            line = cart.add_product(supplier=supplier, shop=shop, product=product, quantity=q)
            assert line.quantity == q
            assert cart.get_lines()
            assert cart.get_product_ids_and_quantities().get(product.pk) == q
            assert cart.product_count == q
            cart.save()
            delattr(request, "cart")
            cart = get_cart(request)
            assert cart.get_product_ids_and_quantities().get(product.pk) == q
            if is_database:
                product_ids = set(StoredCart.objects.last().products.values_list("id", flat=True))
                assert product_ids == set([product.pk])

        if is_database:
            stats = StoredCart.objects.all().aggregate(
                n=Sum("product_count"),
                tfs=Sum("taxful_total_price_value"),
                tls=Sum("taxless_total_price_value"),
            )
            assert stats["n"] == sum(quantities)
            if shop.prices_include_tax:
                assert stats["tfs"] == sum(quantities) * 50
            else:
                assert stats["tls"] == sum(quantities) * 50

        cart.finalize()


@pytest.mark.django_db
def test_cart_dirtying_with_fnl(rf):
    shop = get_default_shop()
    supplier = get_default_supplier()
    product = create_product(printable_gibberish(), shop=shop, supplier=supplier, default_price=50)
    request = rf.get("/")
    request.session = {}
    request.shop = shop
    apply_request_middleware(request)
    cart = get_cart(request)
    line = cart.add_product(
        supplier=supplier,
        shop=shop,
        product=product,
        quantity=1,
        force_new_line=True,
        extra={"foo": "foo"}
    )
    assert cart.dirty  # The change should have dirtied the cart


@pytest.mark.django_db
def test_cart_shipping_error(rf):
    StoredCart.objects.all().delete()
    shop = get_default_shop()
    supplier = get_default_supplier()
    shipped_product = create_product(
        printable_gibberish(), shop=shop, supplier=supplier, default_price=50,
        shipping_mode=ShippingMode.SHIPPED
    )
    unshipped_product = create_product(
        printable_gibberish(), shop=shop, supplier=supplier, default_price=50,
        shipping_mode=ShippingMode.NOT_SHIPPED
    )

    request = rf.get("/")
    request.session = {}
    request.shop = shop
    apply_request_middleware(request)
    cart = get_cart(request)

    # With a shipped product but no shipping methods, we oughta get an error
    cart.add_product(supplier=supplier, shop=shop, product=shipped_product, quantity=1)
    assert any(ve.code == "no_common_shipping" for ve in cart.get_validation_errors())
    cart.clear_all()

    # But with an unshipped product, we should not
    cart.add_product(supplier=supplier, shop=shop, product=unshipped_product, quantity=1)
    assert not any(ve.code == "no_common_shipping" for ve in cart.get_validation_errors())
