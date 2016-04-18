# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.

from shoop.utils import update_module_attributes

from ._cart import cart_partial
from ._product_preview import product_preview
from ._product_price import product_price
from ._products_view import products

__all__ = [
    "cart_partial",
    "product_preview",
    "products",
    "product_price"
]

update_module_attributes(__all__, __name__)
