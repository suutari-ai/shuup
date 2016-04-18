# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.

#: Spec string for the class used for creating Order from a Cart.
#:
#: This is the easiest way to customize the order creation process
#: without having to override a single URL or touch the ``shoop.front`` code.
SHOOP_CART_ORDER_CREATOR_SPEC = (
    "shoop.front.cart.order_creator:CartOrderCreator")

#: Spec string for the Django CBV (or an API-compliant class) for the cart view.
#:
#: This view deals with ``/cart/``.
SHOOP_CART_VIEW_SPEC = (
    "shoop.front.views.cart:DefaultCartView")

#: Spec string for the command dispatcher used when products are added/deleted/etc.
#: from the cart.
#:
#: This view deals with commands ``POST``ed to ``/cart/``.
SHOOP_CART_COMMAND_DISPATCHER_SPEC = (
    "shoop.front.cart.command_dispatcher:CartCommandDispatcher")

#: Spec string for the update method dispatcher used when the cart is updated (usually
#: on the cart page).
SHOOP_CART_UPDATE_METHODS_SPEC = (
    "shoop.front.cart.update_methods:CartUpdateMethods")

#: Spec string for the cart class used in the frontend.
#:
#: This is used to customize the behavior of the cart for a given installation,
#: for instance to modify prices of products based on certain conditions, etc.
SHOOP_CART_CLASS_SPEC = (
    "shoop.front.cart.objects:Cart")

#: The spec string defining which cart storage class to use for the frontend.
#:
#: Cart storages are responsible for persisting visitor cart state, whether
#: in the database (DatabaseCartStorage) or directly in the session
#: (DirectSessionCartStorage).  Custom storage backends could use caches, flat
#: files, etc. if required.
SHOOP_CART_STORAGE_CLASS_SPEC = (
    "shoop.front.cart.storage:DatabaseCartStorage")

#: Spec string for the Django CBV (or an API-compliant class) for the checkout view.
#:
#: This is used to customize the behavior of the checkout process; most likely to
#: switch in a view with a different ``phase_specs``.
SHOOP_CHECKOUT_VIEW_SPEC = (
    "shoop.front.views.checkout:DefaultCheckoutView")

#: Whether Shoop uses its own error handlers.
#:
#: If this value is set to ``False`` django defaults are used or the ones specified
#: in ``settings.ROOT_URLCONF`` file.
#:
#: Setting this to ``True`` won't override handlers specified
#: in ``settings.ROOT_URLCONF``.
#:
#: Handled error cases are: 400, 403, 404, and 500
SHOOP_FRONT_INSTALL_ERROR_HANDLERS = True
