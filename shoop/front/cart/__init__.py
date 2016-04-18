# -*- coding: utf-8 -*-
# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
from shoop.utils.importing import cached_load


def get_cart_order_creator(request=None):
    return cached_load("SHOOP_CART_ORDER_CREATOR_SPEC")(request=request)


def get_cart_view():
    view = cached_load("SHOOP_CART_VIEW_SPEC")
    if hasattr(view, "as_view"):  # pragma: no branch
        view = view.as_view()
    return view


def get_cart_command_dispatcher(request):
    """
    :type request: django.http.request.HttpRequest
    :rtype: shoop.front.cart.command_dispatcher.CartCommandDispatcher
    """
    return cached_load("SHOOP_CART_COMMAND_DISPATCHER_SPEC")(request=request)


def get_cart(request):
    """
    :type request: django.http.request.HttpRequest
    :rtype: shoop.front.cart.objects.Cart
    """
    if not hasattr(request, "cart"):
        cart_class = cached_load("SHOOP_CART_CLASS_SPEC")
        # This is a little weird in that this is likely to be called from `CartMiddleware`,
        # which would do the following assignment anyway. However, in case it's _not_ called
        # from there, for some reason, we want to still be able to cache the cart.
        request.cart = cart_class(request)
    return request.cart
