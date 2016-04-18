# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
from django.db import models
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from polymorphic.models import PolymorphicModel

from shoop.core.fields import MoneyValueField
from shoop.core.models import Contact, ContactGroup, Product
from shoop.utils.properties import MoneyPropped, PriceProperty


class CartCondition(PolymorphicModel):
    model = None
    active = models.BooleanField(default=True)
    name = _("Cart condition")

    def matches(self, cart, lines):
        return False

    def __str__(self):
        return force_text(self.name)


class CartTotalProductAmountCondition(CartCondition):
    identifier = "cart_product_condition"
    name = _("Cart product count")

    product_count = models.DecimalField(
        verbose_name=_("product count in cart"), blank=True, null=True, max_digits=36, decimal_places=9)

    def matches(self, cart, lines):
        return (cart.product_count >= self.product_count)

    @property
    def description(self):
        return _("Limit the campaign to match when cart has at least the product count entered here.")

    @property
    def value(self):
        return self.product_count

    @value.setter
    def value(self, value):
        self.product_count = value


class CartTotalAmountCondition(MoneyPropped, CartCondition):
    identifier = "cart_amount_condition"
    name = _("Cart total value")

    amount = PriceProperty("amount_value", "campaign.shop.currency", "campaign.shop.prices_include_tax")
    amount_value = MoneyValueField(default=None, blank=True, null=True, verbose_name=_("cart total amount"))

    def matches(self, cart, lines):
        return (cart.total_price_of_products.value >= self.amount_value)

    @property
    def description(self):
        return _("Limit the campaign to match when it has at least the total value entered here worth of products.")

    @property
    def value(self):
        return self.amount_value

    @value.setter
    def value(self, value):
        self.amount_value = value


class ProductsInCartCondition(CartCondition):
    identifier = "cart_products_condition"
    name = _("Products in cart")

    model = Product

    products = models.ManyToManyField(Product, verbose_name=_("products"), blank=True)

    def matches(self, cart, lines):
        return any((product_id in cart.product_ids) for product_id in self.products.values_list("pk", flat=True))

    @property
    def description(self):
        return _("Limit the campaign to have the selected products in cart.")

    @property
    def values(self):
        return self.products

    @values.setter
    def values(self, value):
        self.products = value


class ContactGroupCartCondition(CartCondition):
    model = ContactGroup
    identifier = "cart_contact_group_condition"
    name = _("Contact Group")

    contact_groups = models.ManyToManyField(ContactGroup, verbose_name=_("contact groups"))

    def matches(self, cart, lines=[]):
        customers_groups = cart.customer.groups.all()
        return self.contact_groups.filter(pk__in=customers_groups).exists()

    @property
    def description(self):
        return _("Limit the campaign to members of the selected contact groups.")

    @property
    def values(self):
        return self.contact_groups

    @values.setter
    def values(self, values):
        self.contact_groups = values


class ContactCartCondition(CartCondition):
    model = Contact
    identifier = "cart_contact_condition"
    name = _("Contact")

    contacts = models.ManyToManyField(Contact, verbose_name=_("contacts"))

    def matches(self, cart, lines=[]):
        customer = cart.customer
        return bool(customer and self.contacts.filter(pk=customer.pk).exists())

    @property
    def description(self):
        return _("Limit the campaign to selected contacts.")

    @property
    def values(self):
        return self.contacts

    @values.setter
    def values(self, values):
        self.contacts = values
