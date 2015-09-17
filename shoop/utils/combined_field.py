"""
CombinedField for use in Django models.
"""
from collections import OrderedDict

from django.db import models
import six

__all__ = ['CombinedField']


class _FieldCollectMeta(type):
    def __init__(self, name, bases, attrs):
        fields = [
            (v, k) for (k, v) in attrs.items()
            if isinstance(v, models.Field)
        ]
        self._subfields = OrderedDict((k, v) for (v, k) in sorted(fields))
        super(_FieldCollectMeta, self).__init__(name, bases, attrs)


class FieldCollector(six.with_metaclass(_FieldCollectMeta)):
    pass


class CombinedField(models.Field, FieldCollector):
    """
    Model field that combines several fields to one accessor.

    To create a concrete combined field, derive from this class and
    implemend compose_object and decompose_object methods.
    """
    auto_created = False
    concrete = False
    editable = False
    hidden = False
    is_relation = False

    def contribute_to_class(self, cls, name, **kwargs):
        kwargs.setdefault('virtual_only', True)
        super(CombinedField, self).contribute_to_class(cls, name, **kwargs)
        self.field_names = self._get_field_names()
        for (subname, field_name) in self.field_names:
            cls.add_to_class(field_name, self._subfields[subname])
        setattr(cls, name, self)

    def _get_field_names(self):
        return [
            (subname, self.name + '_' + subname)
            for (subname, subfield) in self._subfields.items()
        ]

    def get_attname_column(self):
        return (self.get_attname(), None)

    def get_db_prep_save(self, value):
        pass

    def get_db_prep_lookup(self, lookup_type, value):
        raise NotImplementedError()

    def __get__(self, instance, type=None):
        if instance is None:
            return self
        data = {
            name: getattr(instance, field_name)
            for (name, field_name) in self.field_names
        }
        return self.compose_object(data)

    def __set__(self, instance, value):
        data = self.decompose_object(value)
        for (name, field_name) in self.field_names:
            setattr(instance, field_name, data[name])

    def compose_object(self, data):
        """
        Convert dictionary to object value.

        :param data: Dict from field names to their values.
        :type data: dict[str, Any]
        :rtype: Any
        """
        raise NotImplementedError

    def decompose_object(self, obj):
        """
        Convert object value to dictionary.

        :param obj: Object to convert
        :type obj: Any
        :rtype: dict[str, Any]
        """
        raise NotImplementedError
