# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='config',
            name='id',
        ),
        migrations.AddField(
            model_name='config',
            name='des',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='config',
            name='version',
            field=models.CharField(max_length=255, serialize=False, primary_key=True),
        ),
    ]
