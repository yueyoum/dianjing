# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import apps.system.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bulletin',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name=b'\xe6\xa0\x87\xe9\xa2\x98')),
                ('content', models.TextField(verbose_name=b'\xe5\x86\x85\xe5\xae\xb9', blank=True)),
                ('image', models.FileField(upload_to=apps.system.models.upload_to, null=True, verbose_name=b'\xe5\x9b\xbe\xe7\x89\x87', blank=True)),
                ('order_num', models.IntegerField(default=1, help_text=b'\xe6\x95\xb0\xe5\xad\x97\xe8\xb6\x8a\xe5\xa4\xa7\xe8\xb6\x8a\xe9\x9d\xa0\xe5\x89\x8d', verbose_name=b'\xe6\x8e\x92\xe5\x88\x97\xe5\xba\x8f\xe5\x8f\xb7', db_index=True)),
                ('display', models.BooleanField(default=True, db_index=True, verbose_name=b'\xe6\x98\xaf\xe5\x90\xa6\xe6\x98\xbe\xe7\xa4\xba')),
            ],
            options={
                'db_table': 'bulletin',
                'verbose_name': '\u516c\u544a',
                'verbose_name_plural': '\u516c\u544a',
            },
        ),
    ]
