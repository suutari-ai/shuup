from shoop.core.pricing import Price, TaxfulPrice, TaxlessPrice
from shoop.utils.money import Money
from shoop.utils.numbers import UnitMixupError


class MoneyProperty(object):
    """
    TODO: (TAX) Document MoneyProperty.
    """
    value_class = Money

    def __init__(self, value, currency):
        self._fields = {'value': value, 'currency': currency}

    def __repr__(self):
        argstr = ', '.join('%s=%r' % x for x in self._fields.items())
        return "%s(%s)" % (type(self).__name__, argstr)

    def __get__(self, instance, type=None):
        if instance is None:
            return self
        return self._get_value_from(instance)

    def _get_value_from(self, instance, overrides={}):
        data = {
            field: resolve(instance, path)
            for (field, path) in self._fields.items()
        }
        data.update(overrides)
        if data['value'] is None:
            return None
        return self.value_class.from_data(**data)

    def __set__(self, instance, value):
        self._check_unit(instance, value)
        self._set_part(instance, 'value', value)

    def _check_unit(self, instance, value):
        value_template = self._get_value_from(instance, overrides={'value': 0})
        if not value_template.unit_matches_with(value):
            msg = 'Cannot set %s to value with non-matching unit' % (
                type(self).__name__,)
            raise UnitMixupError(value_template, value, msg)
        assert isinstance(value, self.value_class)

    def _set_part(self, instance, part_name, value):
        value_full_path = self._fields[part_name]
        if '.' in value_full_path:
            (obj_path, attr_to_set) = value_full_path.rsplit('.', 1)
            obj = resolve(instance, obj_path)
        else:
            attr_to_set = value_full_path
            obj = instance
        setattr(obj, attr_to_set, getattr(value, part_name))


class PriceProperty(MoneyProperty):
    """
    TODO: (TAX) Document PriceProperty.
    """
    value_class = Price

    def __init__(self, value, currency, includes_tax, **kwargs):
        super(PriceProperty, self).__init__(value, currency, **kwargs)
        self._fields['includes_tax'] = includes_tax


class TaxfulPriceProperty(MoneyProperty):
    value_class = TaxfulPrice


class TaxlessPriceProperty(MoneyProperty):
    value_class = TaxlessPrice


def resolve(obj, path):
    if path:
        for name in path.split('.'):
            obj = getattr(obj, name, None)
    return obj
