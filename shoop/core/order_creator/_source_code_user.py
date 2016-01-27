# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import unicode_literals

import abc

import six

from shoop.apps.provides import load_module_instances


def is_code_usable(order_source, code):
    return any(
        module.can_use_code(order_source, code)
        for module in get_order_source_code_user_modules()
    )


def get_order_source_code_user_modules():
    """
    Get a list of configured order source code user module instances.

    :rtype: list[OrderSourceCodeUserModule]
    """
    return load_module_instances(
        "SHOOP_ORDER_SOURCE_CODE_USER_MODULES",
        "order_source_code_user_module")


class OrderSourceCodeUserModule(six.with_metaclass(abc.ABCMeta)):
    @abc.abstractmethod
    def can_use_code(self, order_source, code):
        pass

    @abc.abstractmethod
    def use_code(self, code, order):
        pass
