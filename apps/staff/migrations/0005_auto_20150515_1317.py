# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0004_auto_20150506_1554'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff',
            name='in_battle',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='staff',
            name='winning_rate',
            field=models.CharField(default=b'{"p": 0, "z": 0, "t": 0}', max_length=255),
        ),

    ]
