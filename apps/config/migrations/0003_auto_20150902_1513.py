# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0002_auto_20150902_1432'),
    ]

    operations = [
        migrations.RenameField(
            model_name='config',
            old_name='cfgdata',
            new_name='config',
        ),
    ]
