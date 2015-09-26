# # This file is part of Shoop.
# #
# # Copyright (c) 2012-2015, Shoop Ltd. All rights reserved.
# #
# # This source code is licensed under the AGPLv3 license found in the
# # LICENSE file in the root directory of this source tree.
# from django.db import models

# from shoop.core.fields import CurrencyField, MoneyValueField
# from shoop.utils.money import Money
# from shoop.utils.virtual_fields import VirtualMoneyField


# # class TestModel(models.Model):
# #     value = MoneyValueField()
# #     currency = CurrencyField()
# #     amount = VirtualMoneyField('value', 'currency')


# # def test_simple_init():
# #     TestModel()


# # def test_init_with_basic_params():
# #     TestModel(value=3, currency='EUR')


# # def test_init_with_amount_param():
# #     m = TestModel(amount=Money(42, 'EUR'))
# #     assert m.amount == Money(42, 'EUR')
# #     assert m.value == 42
# #     m.amount = Money(42, 'USD')
# #     assert m.currency == 'EUR'
