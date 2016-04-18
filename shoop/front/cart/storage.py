# -*- coding: utf-8 -*-
# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import unicode_literals

import abc

import six
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from shoop.core.utils.users import real_user_or_none
from shoop.front.models import StoredCart
from shoop.utils.importing import cached_load


class CartCompatibilityError(Exception):
    pass


class ShopMismatchCartCompatibilityError(CartCompatibilityError):
    pass


class PriceUnitMismatchCartCompatibilityError(CartCompatibilityError):
    pass


class CartStorage(six.with_metaclass(abc.ABCMeta)):
    def load(self, cart):
        """
        Load the given cart's data dictionary from the storage.

        :type cart: shoop.front.cart.objects.Cart
        :rtype: dict
        :raises:
          `CartCompatibilityError` if cart loaded from the storage
          is not compatible with the requested cart.
        """
        stored_cart = self._load_stored_cart(cart)
        if not stored_cart:
            return {}
        if stored_cart.shop_id != cart.shop.id:
            msg = (
                "Cannot load cart of a different Shop ("
                "%s id=%r with Shop=%s, Dest. Cart Shop=%s)" % (
                    type(stored_cart).__name__,
                    stored_cart.id, stored_cart.shop_id, cart.shop.id))
            raise ShopMismatchCartCompatibilityError(msg)
        price_unit_diff = _price_units_diff(stored_cart, cart.shop)
        if price_unit_diff:
            msg = "%s %r: Price unit mismatch with Shop (%s)" % (
                type(stored_cart).__name__, stored_cart.id,
                price_unit_diff)
            raise PriceUnitMismatchCartCompatibilityError(msg)
        return stored_cart.data or {}

    @abc.abstractmethod
    def _load_stored_cart(self, cart):
        """
        Load stored cart for the given cart from the storage.

        The returned object should have ``id``, ``shop_id``,
        ``currency``, ``prices_include_tax`` and ``data`` attributes.

        :type cart: shoop.front.cart.objects.Cart
        :return: Stored cart or None
        """
        pass

    @abc.abstractmethod
    def save(self, cart, data):  # pragma: no cover
        """
        Save the given data dictionary into the storage for the given cart.

        :type cart: shoop.front.cart.objects.Cart
        :type data: dict
        """
        pass

    @abc.abstractmethod
    def delete(self, cart):  # pragma: no cover
        """
        Delete the cart from storage.

        :type cart: shoop.front.cart.objects.Cart
        """
        pass

    def finalize(self, cart):
        """
        Mark the cart as "finalized" (i.e. completed) in the storage.

        The actual semantics of what finalization does are up to each backend.

        :type cart: shoop.front.cart.objects.Cart
        """
        self.delete(cart=cart)


class DirectSessionCartStorage(CartStorage):
    def __init__(self):
        if settings.SESSION_SERIALIZER == "django.contrib.sessions.serializers.JSONSerializer":  # pragma: no cover
            raise ImproperlyConfigured(
                "DirectSessionCartStorage will not work with the JSONSerializer session serializer."
            )

    def save(self, cart, data):
        stored_cart = DictStoredCart.from_cart_and_data(cart, data)
        cart.request.session[cart.cart_name] = stored_cart.as_dict()

    def _load_stored_cart(self, cart):
        stored_cart_dict = cart.request.session.get(cart.cart_name)
        if not stored_cart_dict:
            return None
        return DictStoredCart.from_dict(stored_cart_dict)

    def delete(self, cart):
        cart.request.session.pop(cart.cart_name, None)


class DictStoredCart(object):
    def __init__(self, id, shop_id, currency, prices_include_tax, data):
        self.id = id
        self.shop_id = shop_id
        self.currency = currency
        self.prices_include_tax = prices_include_tax
        self.data = (data or {})

    @classmethod
    def from_cart_and_data(cls, cart, data):
        return cls(
            id=(getattr(cart, "id", None) or cart.cart_name),
            shop_id=cart.shop.id,
            currency=cart.currency,
            prices_include_tax=cart.prices_include_tax,
            data=data,
        )

    @classmethod
    def from_dict(cls, mapping):
        return cls(**mapping)

    def as_dict(self):
        return {
            "id": self.id,
            "shop_id": self.shop_id,
            "currency": self.currency,
            "prices_include_tax": self.prices_include_tax,
            "data": self.data,
        }


class DatabaseCartStorage(CartStorage):
    def _get_session_key(self, cart):
        return "cart_%s_key" % cart.cart_name

    def save(self, cart, data):
        """
        :type cart: shoop.front.cart.objects.Cart
        """
        request = cart.request
        stored_cart = self._get_stored_cart(cart)
        stored_cart.data = data
        stored_cart.taxless_total_price = cart.taxless_total_price_or_none
        stored_cart.taxful_total_price = cart.taxful_total_price_or_none
        stored_cart.product_count = cart.product_count
        stored_cart.customer = (cart.customer or None)
        stored_cart.orderer = (cart.orderer or None)
        stored_cart.creator = real_user_or_none(cart.creator)
        stored_cart.save()
        stored_cart.products = set(cart.product_ids)
        cart_get_kwargs = {"pk": stored_cart.pk, "key": stored_cart.key}
        request.session[self._get_session_key(cart)] = cart_get_kwargs

    def _load_stored_cart(self, cart):
        return self._get_stored_cart(cart)

    def delete(self, cart):
        stored_cart = self._get_stored_cart(cart)
        if stored_cart and stored_cart.pk:
            stored_cart.deleted = True
            stored_cart.save()
        cart.request.session.pop(self._get_session_key(cart), None)

    def finalize(self, cart):
        stored_cart = self._get_stored_cart(cart)
        if stored_cart and stored_cart.pk:
            stored_cart.deleted = True
            stored_cart.finished = True
            stored_cart.save()
        cart.request.session.pop(self._get_session_key(cart), None)

    def _get_stored_cart(self, cart):
        request = cart.request
        cart_get_kwargs = request.session.get(self._get_session_key(cart))
        stored_cart = None
        if cart_get_kwargs:
            stored_cart = StoredCart.objects.filter(deleted=False, **cart_get_kwargs).first()
        if not stored_cart:
            if cart_get_kwargs:
                request.session.pop(self._get_session_key(cart), None)
            stored_cart = StoredCart(
                shop=cart.shop,
                currency=cart.currency,
                prices_include_tax=cart.prices_include_tax,
            )
        return stored_cart


def _price_units_diff(x, y):
    diff = []
    if x.currency != y.currency:
        diff.append('currency: %r vs %r' % (x.currency, y.currency))
    if x.prices_include_tax != y.prices_include_tax:
        diff.append('includes_tax: %r vs %r' % (
            x.prices_include_tax, y.prices_include_tax))
    return ', '.join(diff)


def get_storage():
    """
    Retrieve a cart storage object.

    :return: A cart storage object
    :rtype: CartStorage
    """
    storage_class = cached_load("SHOOP_CART_STORAGE_CLASS_SPEC")
    return storage_class()
