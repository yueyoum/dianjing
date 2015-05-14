# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('league', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leagueclubinfo',
            name='group_id',
            field=models.UUIDField(db_index=True),
        ),
        migrations.AlterField(
            model_name='leaguenpcinfo',
            name='group_id',
            field=models.UUIDField(db_index=True),
        ),
    ]
