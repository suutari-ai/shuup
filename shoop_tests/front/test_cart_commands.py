# -*- coding: utf-8 -*-
# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
import pytest
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http.response import HttpResponseRedirect, JsonResponse

from shoop.core.models import (
    ProductVariationVariable, ProductVariationVariableValue
)
from shoop.front.cart import commands as cart_commands
from shoop.front.cart import get_cart_command_dispatcher
from shoop.front.cart.command_dispatcher import CartCommandDispatcher
from shoop.front.signals import get_cart_command_handler
from shoop.testing.factories import (
    create_product, get_default_product, get_default_shop,
    get_default_supplier
)
from shoop_tests.front.fixtures import get_request_with_cart


class ReturnUrlCartCommandDispatcher(CartCommandDispatcher):
    def postprocess_response(self, command, kwargs, response):
        response["return"] = "/dummy/"
        return response


@pytest.mark.django_db
def test_dne():
    commands = get_cart_command_dispatcher(get_request_with_cart())
    with pytest.raises(Exception):
        commands.handle("_doesnotexist_")


@pytest.mark.django_db
def test_add_and_remove_and_clear():
    product = get_default_product()
    supplier = get_default_supplier()
    request = get_request_with_cart()
    cart = request.cart

    with pytest.raises(ValidationError):
        cart_commands.handle_add(request, cart, product_id=product.pk, quantity=-3)  # Ordering antimatter is not supported

    # These will get merged into one line...
    cart_commands.handle_add(request, cart, **{"product_id": product.pk, "quantity": 1, "supplier_id": supplier.pk})
    cart_commands.handle_add(request, cart, **{"product_id": product.pk, "quantity": 2})
    # ... so there will be 3 products but one line
    assert cart.product_count == 3
    lines = cart.get_lines()
    assert len(lines) == 1
    # ... and deleting that line will clear the cart...
    cart_commands.handle_del(request, cart, lines[0].line_id)
    assert cart.product_count == 0
    # ... and adding another product will create a new line...
    cart_commands.handle_add(request, cart, product_id=product.pk, quantity=1)
    assert cart.product_count == 1
    # ... that can be cleared.
    cart_commands.handle_clear(request, cart)
    assert cart.product_count == 0

@pytest.mark.django_db
def test_ajax():
    product = get_default_product()
    commands = get_cart_command_dispatcher(get_request_with_cart())
    commands.ajax = True
    rv = commands.handle("add", kwargs=dict(product_id=product.pk, quantity=-3))
    assert isinstance(rv, JsonResponse)
    assert commands.cart.product_count == 0

@pytest.mark.django_db
def test_nonajax():
    product = get_default_product()
    commands = get_cart_command_dispatcher(get_request_with_cart())
    commands.ajax = False
    with pytest.raises(Exception):
        commands.handle("add", kwargs=dict(product_id=product.pk, quantity=-3))

@pytest.mark.django_db
def test_redirect():
    commands = ReturnUrlCartCommandDispatcher(request=get_request_with_cart())
    commands.ajax = False
    assert isinstance(commands.handle("clear"), HttpResponseRedirect)

@pytest.mark.django_db
def test_variation():
    request = get_request_with_cart()
    cart = request.cart
    shop = get_default_shop()
    supplier = get_default_supplier()
    parent = create_product("BuVarParent", shop=shop, supplier=supplier)
    child = create_product("BuVarChild", shop=shop, supplier=supplier)
    child.link_to_parent(parent, variables={"test": "very"})
    attr = parent.variation_variables.get(identifier="test")
    val = attr.values.get(identifier="very")
    cart_commands.handle_add_var(request, cart, 1, **{"var_%s" % attr.id: val.id})
    assert cart.get_product_ids_and_quantities()[child.pk] == 1
    with pytest.raises(ValidationError):
        cart_commands.handle_add_var(request, cart, 1, **{"var_%s" % attr.id: (val.id + 1)})


@pytest.mark.django_db
def test_complex_variation():
    request = get_request_with_cart()
    cart = request.cart
    shop = get_default_shop()
    supplier = get_default_supplier()

    parent = create_product("SuperComplexVarParent", shop=shop, supplier=supplier)
    color_var = ProductVariationVariable.objects.create(product=parent, identifier="color")
    size_var = ProductVariationVariable.objects.create(product=parent, identifier="size")

    ProductVariationVariableValue.objects.create(variable=color_var, identifier="yellow")
    ProductVariationVariableValue.objects.create(variable=size_var, identifier="small")

    combinations = list(parent.get_all_available_combinations())
    for combo in combinations:
        child = create_product("xyz-%s" % combo["sku_part"], shop=shop, supplier=supplier)
        child.link_to_parent(parent, combo["variable_to_value"])

    # Elided product should not yield a result
    yellow_color_value = ProductVariationVariableValue.objects.get(variable=color_var, identifier="yellow")
    small_size_value = ProductVariationVariableValue.objects.get(variable=size_var, identifier="small")

    # add to cart yellow + small
    kwargs = {"var_%d" % color_var.pk: yellow_color_value.pk, "var_%d" % size_var.pk: small_size_value.pk}

    cart_commands.handle_add_var(request, cart, 1, **kwargs)
    assert cart.get_product_ids_and_quantities()[child.pk] == 1

    with pytest.raises(ValidationError):
        kwargs = {"var_%d" % color_var.pk: yellow_color_value.pk, "var_%d" % size_var.pk: small_size_value.pk + 1}
        cart_commands.handle_add_var(request, cart, 1, **kwargs)


@pytest.mark.django_db
def test_cart_update():
    request = get_request_with_cart()
    cart = request.cart
    product = get_default_product()
    cart_commands.handle_add(request, cart, product_id=product.pk, quantity=1)
    assert cart.product_count == 1
    line_id = cart.get_lines()[0].line_id
    cart_commands.handle_update(request, cart, **{"q_%s" % line_id: "2"})
    assert cart.product_count == 2
    cart_commands.handle_update(request, cart, **{"delete_%s" % line_id: "1"})
    assert cart.product_count == 0


@pytest.mark.django_db
def test_cart_update_errors():
    request = get_request_with_cart()
    cart = request.cart
    product = get_default_product()
    cart_commands.handle_add(request, cart, product_id=product.pk, quantity=1)

    # Hide product and now updating quantity should give errors
    shop_product = product.get_shop_instance(request.shop)
    shop_product.suppliers.clear()

    line_id = cart.get_lines()[0].line_id
    cart_commands.handle_update(request, cart, **{"q_%s" % line_id: "2"})
    error_messages = messages.get_messages(request)
    # One warning is added to messages
    assert len(error_messages) == 1
    assert any("not supplied" in msg.message for msg in error_messages)

    shop_product.visible = False
    shop_product.save()

    cart_commands.handle_update(request, cart, **{"q_%s" % line_id: "2"})

    error_messages = messages.get_messages(request)
    # Two warnings is added to messages
    assert len(error_messages) == 3
    assert any("not visible" in msg.message for msg in error_messages)
    assert all("[" not in msg.message for msg in error_messages)


@pytest.mark.django_db
def test_custom_cart_command():
    ok = []
    def noop(**kwargs):
        ok.append(kwargs)
    def get_custom_command(command, **kwargs):
        if command == "test_custom_cart_command":
            return noop
    old_n_receivers = len(get_cart_command_handler.receivers)
    try:
        get_cart_command_handler.connect(get_custom_command, dispatch_uid="test_custom_cart_command")
        commands = get_cart_command_dispatcher(request=get_request_with_cart())
        commands.handle("test_custom_cart_command")
        assert ok  # heh.
    finally:
        get_cart_command_handler.disconnect(dispatch_uid="test_custom_cart_command")
        assert old_n_receivers == len(get_cart_command_handler.receivers)
