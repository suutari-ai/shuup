from decimal import Decimal

from django.utils import translation

from shuup.core.models._units import DisplayableUnit, DisplayUnit


def nbsp(x):
    """
    Convert space to non-breaking space.
    """
    return x.replace(" ", "\xa0")


def test_displayable_unit_smoke():
    kilo = get_kg_displayed_as_g(decimals=4, display_decimals=1)
    assert kilo.symbol == 'kg'
    assert kilo.display_symbol == 'g'
    assert kilo.to_display(Decimal('0.01')) == 10
    assert kilo.from_display(10) == Decimal('0.01')
    assert kilo.render_quantity(Decimal('0.01')) == '10.0g'
    assert kilo.comparison_quantity == Decimal('0.1')
    assert kilo.comparison_quantity_text == '100.0g'


def test_displayable_unit_to_display():
    kilo3 = get_kg_displayed_as_g(decimals=3, display_decimals=0)
    assert kilo3.to_display(Decimal('0.01')) == 10
    assert kilo3.to_display(Decimal('0.001')) == 1
    assert kilo3.to_display(Decimal('0.0005')) == 1
    assert kilo3.to_display(Decimal('0.000499')) == 0
    assert kilo3.to_display(Decimal('-1')) == -1000
    assert kilo3.to_display(Decimal('-0.1234')) == -123
    assert kilo3.to_display(Decimal('-0.1235')) == -124


def test_displayable_unit_to_display_small_display_prec():
    kilo6 = get_kg_displayed_as_g(decimals=6, display_decimals=1)
    assert kilo6.to_display(Decimal('0.01')) == 10
    assert kilo6.to_display(Decimal('0.001')) == 1
    assert kilo6.to_display(Decimal('0.0005')) == Decimal('0.5')
    assert kilo6.to_display(Decimal('0.000499')) == Decimal('0.499')
    assert kilo6.to_display(Decimal('0.0001234')) == Decimal('0.123')
    assert kilo6.to_display(Decimal('0.0001235')) == Decimal('0.124')
    assert kilo6.to_display(Decimal('12.3456789')) == Decimal('12345.679')


def test_displayable_unit_to_display_float():
    kilo3 = get_kg_displayed_as_g(decimals=3, display_decimals=0)
    assert kilo3.to_display(0.01) == 10


def test_displayable_unit_to_display_str():
    kilo3 = get_kg_displayed_as_g(decimals=3, display_decimals=0)
    assert kilo3.to_display('0.01') == 10


def test_displayable_unit_from_display():
    kilo3 = get_kg_displayed_as_g(decimals=3, display_decimals=0)
    assert kilo3.from_display(1234) == Decimal('1.234')
    assert kilo3.from_display(Decimal('123.456')) == Decimal('0.123')
    assert kilo3.from_display(Decimal('123.5')) == Decimal('0.124')
    assert kilo3.from_display(Decimal('124.5')) == Decimal('0.125')


def test_displayable_unit_from_display_small_display_prec():
    kilo6 = get_kg_displayed_as_g(decimals=6, display_decimals=1)
    assert kilo6.from_display(123) == Decimal('0.123')
    assert kilo6.from_display(Decimal('123.456')) == Decimal('0.123456')
    assert kilo6.from_display(Decimal('123.4565')) == Decimal('0.123457')


def test_displayable_unit_from_display_float():
    kilo6 = get_kg_displayed_as_g(decimals=6, display_decimals=3)
    assert kilo6.from_display(123.456) == Decimal('0.123456')


def test_displayable_unit_from_display_str():
    kilo6 = get_kg_displayed_as_g(decimals=6, display_decimals=3)
    assert kilo6.from_display('123.456') == Decimal('0.123456')


def test_displayable_unit_render_quantity():
    kilo3 = get_kg_displayed_as_g(decimals=3, display_decimals=0)
    with translation.override(None):
        assert kilo3.render_quantity(123) == '123000g'
        assert kilo3.render_quantity(0.123) == '123g'
        assert kilo3.render_quantity('0.0521') == '52g'
        assert kilo3.render_quantity('0.0525') == '53g'
        assert kilo3.render_quantity('0.0535') == '54g'


def test_displayable_unit_render_quantity_small_display_prec():
    kilo6 = get_kg_displayed_as_g(decimals=6, display_decimals=1)
    with translation.override(None):
        assert kilo6.render_quantity(Decimal('12.3456789')) == '12345.7g'


def test_displayable_unit_render_quantity_translations():
    kilo = get_kg_displayed_as_g(decimals=7, display_decimals=4)
    qty = Decimal('4321.1234567')
    with translation.override(None):
        assert kilo.render_quantity(qty) == '4321123.4567g'
    with translation.override('en'):
        assert kilo.render_quantity(qty) == '4,321,123.4567g'
    with translation.override('fi'):
        assert kilo.render_quantity(qty) == nbsp('4 321 123,4567g')
    with translation.override('pt-br'):
        assert kilo.render_quantity(qty) == '4.321.123,4567g'
    with translation.override('hi'):
        assert kilo.render_quantity(qty) == '43,21,123.4567g'
    with translation.override('hy'):
        assert kilo.render_quantity(qty) == '4321123,4567g'


def get_kg_displayed_as_g(decimals, display_decimals, comparison=100):
    return Kilogram(
        decimals=decimals,
        display_unit=DisplayUnit(
            multiplier=Decimal(1000),
            decimals=display_decimals,
            symbol='g',
            comparison_quantity=comparison,
        )
    )


class Kilogram(DisplayableUnit):
    def __init__(self, decimals, display_unit):
        self.name = "Kilograms"
        self.symbol = 'kg'
        self.decimals = decimals
        self.display_unit = display_unit
