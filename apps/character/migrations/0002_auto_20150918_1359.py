# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='character',
            options={'ordering': ('last_login',)},
        ),
        migrations.AddField(
            model_name='character',
            name='last_login',
            field=models.DateTimeField(default='2015-09-18 13:58:47+0800', auto_now=True, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='character',
            name='login_times',
            field=models.BigIntegerField(default=0),
        ),
    ]
