# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=32)),
                ('status', models.IntegerField(default=1, choices=[(1, b'\xe6\x96\xb0'), (2, b'\xe7\x81\xab')])),
                ('open_at', models.DateTimeField(db_index=True)),
            ],
            options={
                'db_table': 'server',
            },
        ),
    ]
