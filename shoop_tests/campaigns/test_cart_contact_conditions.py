# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
import pytest

from django.utils.translation import activate

from shoop.campaigns.models.campaigns import CartCampaign
from shoop.campaigns.models.cart_conditions import (
    ContactCartCondition, ContactGroupCartCondition
)
from shoop.core.models import AnonymousContact, Shop
from shoop.front.cart import get_cart
from shoop.testing.factories import (
    create_product, create_random_person, get_default_customer_group,
    get_default_supplier, get_payment_method, get_shop,
)
from shoop.testing.utils import apply_request_middleware


def get_request_for_contact_tests(rf):
    activate("en")
    request = rf.get("/")
    request.shop = get_shop(prices_include_tax=True)
    get_payment_method(request.shop)
    apply_request_middleware(request)
    return request


def create_cart_and_campaign(request, conditions, product_price_value, campaign_discount_value):
    product = create_product(
        "Some crazy product", request.shop, get_default_supplier(), default_price=product_price_value)
    cart = get_cart(request)
    cart.customer = request.customer
    supplier = get_default_supplier()
    cart.add_product(supplier=supplier, shop=request.shop, product=product, quantity=1)

    original_line_count = len(cart.get_final_lines())
    assert original_line_count == 1
    assert cart.product_count == 1
    original_price = cart.total_price

    campaign = CartCampaign.objects.create(
        shop=request.shop, name="test", public_name="test", discount_amount_value=campaign_discount_value, active=True)
    for condition in conditions:
        campaign.conditions.add(condition)
    assert campaign.is_available()

    return cart, original_line_count, original_price


def assert_discounted_cart(cart, original_line_count, original_price, campaign_discount_value):
    cart.uncache()
    price = cart.shop.create_price
    assert len(cart.get_final_lines()) == original_line_count + 1
    assert cart.total_price == original_price - price(campaign_discount_value)


def assert_non_discounted_cart(cart, original_line_count, original_price):
    cart.uncache()
    assert len(cart.get_final_lines()) == original_line_count
    assert cart.total_price == original_price


@pytest.mark.django_db
def test_cart_contact_group_condition(rf):
    product_price_value, campaign_discount_value = 123, 15
    request = get_request_for_contact_tests(rf)
    customer = create_random_person()
    default_group = get_default_customer_group()
    customer.groups.add(default_group)
    request.customer = customer

    condition = ContactGroupCartCondition.objects.create()
    condition.contact_groups.add(default_group)
    cart, original_line_count, original_price = create_cart_and_campaign(
        request, [condition], product_price_value, campaign_discount_value)

    assert cart.customer == customer
    assert_discounted_cart(cart, original_line_count, original_price, campaign_discount_value)

    customer.groups.remove(default_group)
    assert_non_discounted_cart(cart, original_line_count, original_price)


@pytest.mark.django_db
def test_group_cart_condition_with_anonymous_contact(rf):
    product_price_value, campaign_discount_value = 6, 4
    request = get_request_for_contact_tests(rf)
    assert isinstance(request.customer, AnonymousContact)
    condition = ContactGroupCartCondition.objects.create()
    condition.contact_groups.add(request.customer.groups.first())

    cart, original_line_count, original_price = create_cart_and_campaign(
        request, [condition], product_price_value, campaign_discount_value)

    assert isinstance(cart.customer, AnonymousContact)
    assert_discounted_cart(cart, original_line_count, original_price, campaign_discount_value)


@pytest.mark.django_db
def test_contact_group_cart_condition_with_none(rf):
    request = rf.get("/")
    request.shop = Shop()
    cart = get_cart(request)
    condition = ContactGroupCartCondition.objects.create()
    result = condition.matches(cart)  # Should not raise any errors
    assert result is False


@pytest.mark.django_db
def test_cart_contact_condition(rf):
    product_price_value, campaign_discount_value = 2, 1
    request = get_request_for_contact_tests(rf)
    random_person = create_random_person()
    request.customer = random_person
    condition = ContactCartCondition.objects.create()
    condition.contacts.add(random_person)
    cart, original_line_count, original_price = create_cart_and_campaign(
        request, [condition], product_price_value, campaign_discount_value)

    # random_person should get this campaign
    assert cart.customer == random_person
    assert_discounted_cart(cart, original_line_count, original_price, campaign_discount_value)

    another_random_person = create_random_person()
    cart.customer = another_random_person
    # another random person shouldn't
    assert_non_discounted_cart(cart, original_line_count, original_price)

    # Add another random person for the rule and see if he get's the discount
    condition.contacts.add(another_random_person)
    condition.save()
    assert_discounted_cart(cart, original_line_count, original_price, campaign_discount_value)
    assert cart.customer == another_random_person

    # Remove random person from rule and see the discount disappear
    condition.contacts.remove(random_person)
    condition.save()
    cart.customer = random_person
    assert_non_discounted_cart(cart, original_line_count, original_price)
    assert cart.customer == random_person
