# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shoop', '0010_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='tax_group',
            field=models.ForeignKey(to='shoop.CustomerTaxGroup', null=True, blank=True),
        ),
    ]
