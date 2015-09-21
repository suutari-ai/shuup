from django.db import models

from .properties import (
    MoneyProperty, PriceProperty, TaxfulPriceProperty, TaxlessPriceProperty
)


class VirtualField(models.Field):
    auto_created = False
    concrete = True
    editable = False
    hidden = False
    is_relation = False
    primary_key = False

    def contribute_to_class(self, cls, name, **kwargs):
        #kwargs.setdefault('virtual_only', True)
        #super(VirtualField, self).contribute_to_class(cls, name, **kwargs)
        self.name = name
        self.attname = name
        self.rel = None
        self.column = None
        self.concrete = True
        cls._meta.add_field(self)
        setattr(cls, name, self)

    def get_attname_column(self):
        return (self.get_attname(), None)

    def get_db_prep_save(self, value):
        pass

    def get_db_prep_lookup(self, lookup_type, value):
        raise NotImplementedError()


class VirtualMoneyField(MoneyProperty, VirtualField):
    pass


class VirtualPriceField(VirtualField, PriceProperty):
    pass


class VirtualTaxfulPriceField(VirtualField, TaxfulPriceProperty):
    pass


class VirtualTaxlessPriceField(VirtualField, TaxlessPriceProperty):
    pass
