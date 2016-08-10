# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import apps.config.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Config',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('version', models.CharField(max_length=255)),
                ('cfgdata', models.FileField(upload_to=apps.config.models.config_upload_to)),
                ('in_use', models.BooleanField(default=False, db_index=True)),
            ],
            options={
                'db_table': 'config',
            },
        ),
    ]
