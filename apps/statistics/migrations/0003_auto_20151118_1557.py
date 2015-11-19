# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('statistics', '0002_auto_20150917_1943'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='statistics',
            options={'ordering': ['-create_at'], 'verbose_name': '\u8d22\u52a1\u7edf\u8ba1', 'verbose_name_plural': '\u8d22\u52a1\u7edf\u8ba1'},
        ),
    ]
