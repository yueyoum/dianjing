# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_auto_20150918_1359'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='account',
            options={'verbose_name': '\u5e10\u53f7', 'verbose_name_plural': '\u5e10\u53f7'},
        ),
        migrations.AlterModelOptions(
            name='accountregular',
            options={},
        ),
    ]
