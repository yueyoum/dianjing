# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0006_auto_20150515_1322'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staff',
            name='club_id',
            field=models.IntegerField(db_index=True),
        ),
    ]
