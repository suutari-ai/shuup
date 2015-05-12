# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shoop', '0002_auto_20150602_1148'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contact',
            name='prefix',
        ),
        migrations.RemoveField(
            model_name='contact',
            name='suffix',
        ),
        migrations.AddField(
            model_name='personcontact',
            name='first_name',
            field=models.CharField(max_length=30, verbose_name='first name', blank=True),
        ),
        migrations.AddField(
            model_name='personcontact',
            name='last_name',
            field=models.CharField(max_length=50, verbose_name='last name', blank=True),
        ),
        migrations.AddField(
            model_name='personcontact',
            name='prefix',
            field=models.CharField(max_length=64, verbose_name='name prefix', blank=True),
        ),
        migrations.AddField(
            model_name='personcontact',
            name='suffix',
            field=models.CharField(max_length=64, verbose_name='name suffix', blank=True),
        ),
    ]
