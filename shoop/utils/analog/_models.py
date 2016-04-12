# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from enumfields import EnumIntegerField
from jsonfield import JSONField

from ._enums import LogEntryKind


class BaseLogEntry(models.Model):
    target = None  # This will be overridden dynamically
    created_on = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=_("created on"))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT, verbose_name=_("user"))
    message = models.CharField(max_length=256, verbose_name=_("message"))
    identifier = models.CharField(max_length=64, blank=True, verbose_name=_("identifier"))
    kind = EnumIntegerField(LogEntryKind, default=LogEntryKind.OTHER, verbose_name=_("log entry kind"))
    extra = JSONField(null=True, blank=True, verbose_name=_("extra data"))

    class Meta:
        abstract = True
