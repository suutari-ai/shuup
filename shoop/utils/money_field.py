from django.db import models

from . import combined_field
from . import money


class MoneyField(combined_field.CombinedField):
    auto_created = False
    concrete = False
    editable = False
    hidden = False
    is_relation = False

    value = models.DecimalField(max_digits=36, decimal_places=9)

    #def __init__(self, *args, **kwargs):
    #    pass#TODO

    def contribute_to_class(self, cls, name, **kwargs):
        kwargs.setdefault('virtual_only', True)
        super(MoneyField, self).contribute_to_class(cls, name, **kwargs)
        self.field_names = self._get_field_names()
        cls.add_to_class(name + '_value', self.value)
        setattr(cls, name, self)

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

    @classmethod
    def compose_object(cls, data):
        return money.Money(data['value'], currency=data['currency'])

    @classmethod
    def decompose_object(cls, obj):
        if obj is None:
            return {'value': None, 'currency': None}
        if not isinstance(obj, money.Money):
            raise TypeError('Expecting instance of Money')
        return {'value': obj.value, 'currency': obj.currency}
