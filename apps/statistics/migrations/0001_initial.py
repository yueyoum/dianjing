# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Statistics',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, primary_key=True)),
                ('create_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('server_id', models.IntegerField()),
                ('char_id', models.IntegerField(db_index=True)),
                ('club_gold', models.IntegerField(default=0, verbose_name=b'\xe9\x87\x91\xe5\xb8\x81')),
                ('club_diamond', models.IntegerField(default=0, verbose_name=b'\xe9\x92\xbb\xe7\x9f\xb3')),
                ('message', models.CharField(max_length=255, blank=True)),
            ],
            options={
                'db_table': 'statistics',
                'verbose_name': '\u7edf\u8ba1',
                'verbose_name_plural': '\u7edf\u8ba1',
            },
        ),
    ]
