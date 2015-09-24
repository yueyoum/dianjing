# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MailHistoryRecord',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, primary_key=True)),
                ('from_id', models.IntegerField(verbose_name=b'\xe5\x8f\x91\xe9\x80\x81\xe8\x80\x85', db_index=True)),
                ('to_id', models.IntegerField(verbose_name=b'\xe6\x8e\xa5\xe6\x94\xb6\xe8\x80\x85', db_index=True)),
                ('title', models.CharField(max_length=255, verbose_name=b'\xe6\xa0\x87\xe9\xa2\x98')),
                ('content', models.TextField(verbose_name=b'\xe5\x86\x85\xe5\xae\xb9')),
                ('has_read', models.BooleanField(default=False, verbose_name=b'\xe5\xb7\xb2\xe8\xaf\xbb')),
                ('attachment', models.TextField(default=b'', verbose_name=b'\xe9\x99\x84\xe4\xbb\xb6')),
                ('function', models.IntegerField(default=0, verbose_name=b'\xe5\x8a\x9f\xe8\x83\xbd')),
                ('create_at', models.DateTimeField(auto_now_add=True, verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe6\x97\xb6\xe9\x97\xb4')),
            ],
            options={
                'db_table': 'mail_history_record',
                'verbose_name': '\u90ae\u4ef6\u5386\u53f2\u8bb0\u5f55',
                'verbose_name_plural': '\u90ae\u4ef6\u5386\u53f2\u8bb0\u5f55',
            },
        ),
    ]
