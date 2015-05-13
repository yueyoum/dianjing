# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('league', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leaguebattle',
            name='club_one',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='leaguebattle',
            name='club_two',
            field=models.BigIntegerField(default=0),
        ),
    ]
