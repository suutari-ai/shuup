# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.


class ModelInitDataModifier(object):
    """
    Helper for modifying args and kwargs of a Model init function.

    This is useful, because same fields can be set in args and in kwargs
    and if some argument has to be modified, it is non-trivial to change
    args/kwargs correctly.
    """
    def __init__(self, meta, args, kwargs):
        self._meta = meta
        self.args = args
        self.kwargs = kwargs
        assert len(args) <= len(meta.fields)
        self._argsdata = dict((f.name, v) for (f, v) in zip(meta.fields, args))

    def get_all(self, *keys, **kwargs):
        default = kwargs.get('default')
        return tuple(self.get(key, default) for key in keys)

    def get(self, key, default=None):
        if key in self._argsdata:
            return self._argsdata[key]
        return self.kwargs.get(key, default)

    def set(self, key, value):
        if key in self._argsdata:
            self.args = [
                oldval if field.name != key else value
                for (field, oldval) in zip(self._meta.fields, self.args)]
            self._argsdata[key] = value
        else:
            self.kwargs[key] = value
