# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history_record', '0002_auto_20150924_1133'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mailhistoryrecord',
            options={'ordering': ['-create_at'], 'verbose_name': '\u90ae\u4ef6\u5386\u53f2\u8bb0\u5f55', 'verbose_name_plural': '\u90ae\u4ef6\u5386\u53f2\u8bb0\u5f55'},
        ),
        migrations.AlterField(
            model_name='mailhistoryrecord',
            name='create_at',
            field=models.DateTimeField(verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe6\x97\xb6\xe9\x97\xb4', db_index=True),
        ),
        migrations.AlterField(
            model_name='mailhistoryrecord',
            name='id',
            field=models.UUIDField(serialize=False, primary_key=True),
        ),
    ]
