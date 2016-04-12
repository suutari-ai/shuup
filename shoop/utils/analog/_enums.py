# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from enumfields import Enum


class LogEntryKind(Enum):
    OTHER = 0
    AUDIT = 1
    EDIT = 2
    DELETION = 3
    NOTE = 4
    EMAIL = 5
    WARNING = 6
    ERROR = 7

    class Labels:
        OTHER = _("other")
        AUDIT = _("audit")
        EDIT = _("edit")
        DELETION = _("deletion")
        NOTE = _("note")
        EMAIL = _("email")
        WARNING = _("warning")
        ERROR = _("error")
