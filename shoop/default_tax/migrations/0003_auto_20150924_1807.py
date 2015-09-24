# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('default_tax', '0002_auto_20150923_2002'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taxrule',
            name='customer_tax_groups',
            field=models.ManyToManyField(blank=True, to='shoop.CustomerTaxGroup'),
        ),
    ]
