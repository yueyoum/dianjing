# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_auto_20150918_1416'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='account',
            options={'ordering': ['-last_login'], 'verbose_name': '\u5e10\u53f7', 'verbose_name_plural': '\u5e10\u53f7'},
        ),
        migrations.AlterModelOptions(
            name='accountloginlog',
            options={'ordering': ['-login_at'], 'verbose_name': '\u767b\u5f55\u65e5\u5fd7', 'verbose_name_plural': '\u767b\u5f55\u65e5\u5fd7'},
        ),
    ]
