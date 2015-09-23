# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='accountloginlog',
            options={'ordering': ['login_at'], 'verbose_name': '\u767b\u5f55\u65e5\u5fd7', 'verbose_name_plural': '\u767b\u5f55\u65e5\u5fd7'},
        ),
        migrations.AlterModelOptions(
            name='accountregular',
            options={'verbose_name': '\u5e10\u53f7', 'verbose_name_plural': '\u5e10\u53f7'},
        ),
        migrations.AlterField(
            model_name='account',
            name='login_times',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='accountloginlog',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, serialize=False, primary_key=True),
        ),
    ]
