# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('league', '0002_auto_20150515_0216'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaguebattle',
            name='battle_at',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
