# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def copy_prefix_and_suffix(apps, schema_editor):
    person_contact_cls = apps.get_model("shoop", "PersonContact")

    empty_prefix_and_suffix = models.Q(prefix="") & models.Q(suffix="")
    for person in person_contact_cls.objects.exclude(empty_prefix_and_suffix):
        if person.prefix or person.suffix:
            person.new_prefix = person.prefix
            person.new_suffix = person.suffix
            person.save()


class Migration(migrations.Migration):

    dependencies = [
        ('shoop', '0017_contact_group_price_display_options'),
    ]

    operations = [
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
            name='new_prefix',
            field=models.CharField(verbose_name='name prefix', max_length=64, blank=True),
        ),
        migrations.AddField(
            model_name='personcontact',
            name='new_suffix',
            field=models.CharField(verbose_name='name suffix', max_length=64, blank=True),
        ),
        migrations.RunPython(copy_prefix_and_suffix),
        migrations.RemoveField(
            model_name='contact',
            name='prefix',
        ),
        migrations.RemoveField(
            model_name='contact',
            name='suffix',
        ),
        migrations.RenameField(
            model_name='personcontact',
            old_name='new_prefix',
            new_name='prefix',
        ),
        migrations.RenameField(
            model_name='personcontact',
            old_name='new_suffix',
            new_name='suffix',
        ),
    ]
