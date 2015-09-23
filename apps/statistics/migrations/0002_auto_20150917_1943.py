# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('statistics', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='statistics',
            options={'ordering': ['-create_at'], 'verbose_name': '\u7edf\u8ba1', 'verbose_name_plural': '\u7edf\u8ba1'},
        ),
    ]
