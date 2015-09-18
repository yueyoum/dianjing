# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_auto_20150918_1407'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='account',
            options={'ordering': ['last_login'], 'verbose_name': '\u5e10\u53f7', 'verbose_name_plural': '\u5e10\u53f7'},
        ),
    ]
