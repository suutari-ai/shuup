# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal

import pytest
from django.utils import translation
from django.utils.translation.trans_real import translation as get_trans

from shuup.core.models._units import DisplayUnit, UnitAccessor


def nbsp(x):
    """
    Convert space to non-breaking space.
    """
    return x.replace(" ", "\xa0")


def test_unit_accessor_smoke():
    kilo = get_kg_displayed_as_g(decimals=4, display_decimals=1)
    assert kilo.symbol == 'kg'
    assert kilo.display_symbol == 'g'
    assert kilo.to_display(Decimal('0.01')) == 10
    assert kilo.from_display(10) == Decimal('0.01')
    assert kilo.display_quantity(Decimal('0.01')) == '10.0g'
    assert kilo.comparison_quantity == Decimal('0.1')


def test_unit_accessor_to_display():
    kilo3 = get_kg_displayed_as_g(decimals=3, display_decimals=0)
    assert kilo3.to_display(Decimal('0.01')) == 10
    assert kilo3.to_display(Decimal('0.001')) == 1
    assert kilo3.to_display(Decimal('0.0005')) == 1
    assert kilo3.to_display(Decimal('0.000499')) == 0
    assert kilo3.to_display(Decimal('-1')) == -1000
    assert kilo3.to_display(Decimal('-0.1234')) == -123
    assert kilo3.to_display(Decimal('-0.1235')) == -124


def test_unit_accessor_to_display_small_display_prec():
    kilo6 = get_kg_displayed_as_g(decimals=6, display_decimals=1)
    assert kilo6.to_display(Decimal('0.01')) == 10
    assert kilo6.to_display(Decimal('0.001')) == 1
    assert kilo6.to_display(Decimal('0.0005')) == Decimal('0.5')
    assert kilo6.to_display(Decimal('0.000499')) == Decimal('0.499')
    assert kilo6.to_display(Decimal('0.0001234')) == Decimal('0.123')
    assert kilo6.to_display(Decimal('0.0001235')) == Decimal('0.124')
    assert kilo6.to_display(Decimal('12.3456789')) == Decimal('12345.679')


def test_unit_accessor_to_display_float():
    kilo3 = get_kg_displayed_as_g(decimals=3, display_decimals=0)
    assert kilo3.to_display(0.01) == 10


def test_unit_accessor_to_display_str():
    kilo3 = get_kg_displayed_as_g(decimals=3, display_decimals=0)
    assert kilo3.to_display('0.01') == 10


def test_unit_accessor_from_display():
    kilo3 = get_kg_displayed_as_g(decimals=3, display_decimals=0)
    assert kilo3.from_display(1234) == Decimal('1.234')
    assert kilo3.from_display(Decimal('123.456')) == Decimal('0.123')
    assert kilo3.from_display(Decimal('123.5')) == Decimal('0.124')
    assert kilo3.from_display(Decimal('124.5')) == Decimal('0.125')


def test_unit_accessor_from_display_small_display_prec():
    kilo6 = get_kg_displayed_as_g(decimals=6, display_decimals=1)
    assert kilo6.from_display(123) == Decimal('0.123')
    assert kilo6.from_display(Decimal('123.456')) == Decimal('0.123456')
    assert kilo6.from_display(Decimal('123.4565')) == Decimal('0.123457')


def test_unit_accessor_from_display_float():
    kilo6 = get_kg_displayed_as_g(decimals=6, display_decimals=3)
    assert kilo6.from_display(123.456) == Decimal('0.123456')


def test_unit_accessor_from_display_str():
    kilo6 = get_kg_displayed_as_g(decimals=6, display_decimals=3)
    assert kilo6.from_display('123.456') == Decimal('0.123456')


def test_unit_accessor_display_quantity():
    kilo3 = get_kg_displayed_as_g(decimals=3, display_decimals=0)
    with translation.override(None):
        assert kilo3.display_quantity(123) == '123000g'
        assert kilo3.display_quantity(0.123) == '123g'
        assert kilo3.display_quantity('0.0521') == '52g'
        assert kilo3.display_quantity('0.0525') == '53g'
        assert kilo3.display_quantity('0.0535') == '54g'


def test_unit_accessor_display_quantity_small_display_prec():
    kilo6 = get_kg_displayed_as_g(decimals=6, display_decimals=1)
    with translation.override(None):
        assert kilo6.display_quantity(Decimal('12.3456789')) == '12345.7g'


def test_unit_accessor_display_quantity_translations():
    # Let's override some translations, just to be sure
    for lang in ['en', 'pt-br', 'hi', 'hy']:
        get_trans(lang).merge(ValueSymbolTranslationWithoutSpace)
    for lang in ['fi']:
        get_trans(lang).merge(ValueSymbolTranslationWithSpace)

    kilo = get_kg_displayed_as_g(decimals=7, display_decimals=4)
    qty = Decimal('4321.1234567')
    with translation.override(None):
        assert kilo.display_quantity(qty) == '4321123.4567g'
    with translation.override('en'):
        assert kilo.display_quantity(qty) == '4,321,123.4567g'
    with translation.override('fi'):
        assert kilo.display_quantity(qty) == nbsp('4 321 123,4567 g')
    with translation.override('pt-br'):
        assert kilo.display_quantity(qty) == '4.321.123,4567g'
    with translation.override('hi'):
        assert kilo.display_quantity(qty) == '43,21,123.4567g'
    with translation.override('hy'):
        assert kilo.display_quantity(qty) == '4321123,4567g'


trans_key = (
    'Display value with unit symbol (with or without space)'
    '\x04'  # Gettext context separator
    '{value}{symbol}')


class ValueSymbolTranslationWithSpace(object):
    _catalog = {trans_key: nbsp('{value} {symbol}')}


class ValueSymbolTranslationWithoutSpace(object):
    _catalog = {trans_key: '{value}{symbol}'}


def test_kg_in_oz():
    kg_oz = UnitAccessor(
        Kilogram(decimals=9),
        DisplayUnit(
            ratio=Decimal('0.028349523'),
            decimals=3, symbol='oz'))
    assert kg_oz.comparison_quantity == Decimal('0.028349523')
    assert kg_oz.display_quantity('0.028349523') == '1.000oz'
    assert kg_oz.display_quantity(1) == '35.274oz'
    assert kg_oz.display_quantity(0.001) == '0.035oz'
    assert kg_oz.from_display(Decimal('0.001')) == Decimal('0.000028350')
    assert kg_oz.to_display(Decimal('0.000028350')) == approx('0.001')


def approx(value):
    return pytest.approx(Decimal(value), abs=Decimal('0.1')**7)


def get_kg_displayed_as_g(decimals, display_decimals, comparison=100):
    display_unit = DisplayUnit(
        ratio=Decimal('0.001'),
        decimals=display_decimals,
        symbol='g',
        comparison_value=comparison,
    )
    return UnitAccessor(Kilogram(decimals), display_unit)


class Kilogram(object):
    def __init__(self, decimals):
        self.name = "Kilograms"
        self.symbol = 'kg'
        self.decimals = decimals
