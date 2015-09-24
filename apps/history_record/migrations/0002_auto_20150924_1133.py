# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history_record', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mailhistoryrecord',
            name='attachment',
            field=models.TextField(default=b'', verbose_name=b'\xe9\x99\x84\xe4\xbb\xb6', blank=True),
        ),
    ]
