# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shoop', '0020_services_and_methods'),
        ('shoop_front', '0003_verbose_names'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='StoredBasket',
            new_name='StoredCart',
        ),
    ]
