# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0002_auto_20150506_1110'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staff',
            name='id',
            field=models.AutoField(serialize=False, primary_key=True),
        ),
        migrations.AlterField(
            model_name='stafftraining',
            name='id',
            field=models.AutoField(serialize=False, primary_key=True),
        ),
    ]
