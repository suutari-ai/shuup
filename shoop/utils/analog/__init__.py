# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from ._enums import LogEntryKind

all_known_log_models = {}


def get_log_model(model):
    from ._models import BaseLogEntry

    if model is None:
        return BaseLogEntry

    log_model = all_known_log_models.get(model)
    if not log_model:
        return define_log_model(model)
    return log_model


def define_log_model(model_class):
    from ._models import BaseLogEntry

    log_model_name = "%sLogEntry" % model_class.__name__

    class Meta:
        app_label = model_class._meta.app_label
        abstract = False

    class_dict = {
        "target": models.ForeignKey(
            model_class, related_name="log_entries", on_delete=models.CASCADE, verbose_name=_("target")),
        "__module__": model_class.__module__,
        "Meta": Meta,
        "logged_model": model_class,
    }

    log_entry_class = type(str(log_model_name), (BaseLogEntry, ), class_dict)

    def _add_log_entry(self, message, identifier=None, kind=LogEntryKind.OTHER, user=None, extra=None, save=True):
        # You can also pass something that contains "user" as an
        # attribute for an user
        user = (getattr(user, "user", user) or None)
        if not getattr(user, "pk", None):
            user = None
        log_entry = log_entry_class(
            target=self,
            message=message,
            identifier=force_text(identifier or "", errors="ignore")[:64],
            user=user,
            kind=kind,
            extra=(extra or None),
        )
        if save:
            log_entry.save()
        return log_entry

    setattr(model_class, "add_log_entry", _add_log_entry)
    all_known_log_models[model_class] = log_entry_class
    return log_entry_class
