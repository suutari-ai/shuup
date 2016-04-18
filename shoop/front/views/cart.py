# -*- coding: utf-8 -*-
# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
from django.views.generic import TemplateView, View

from shoop.front.cart import get_cart_command_dispatcher, get_cart_view


class DefaultCartView(TemplateView):
    template_name = "shoop/front/cart/default_cart.jinja"

    def get_context_data(self, **kwargs):
        context = super(DefaultCartView, self).get_context_data()
        cart = self.request.cart  # type: shoop.front.cart.objects.Cart
        context["cart"] = cart
        context["errors"] = list(cart.get_validation_errors())
        return context


class CartView(View):
    def dispatch(self, request, *args, **kwargs):
        command = request.REQUEST.get("command")
        if command:
            return get_cart_command_dispatcher(request).handle(command)
        else:
            return get_cart_view()(request, *args, **kwargs)
