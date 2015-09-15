# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0003_auto_20150902_1513'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerServiceInformation',
            fields=[
                ('name', models.CharField(max_length=255, serialize=False, primary_key=True)),
                ('value', models.CharField(max_length=255)),
                ('des', models.TextField(blank=True)),
            ],
            options={
                'db_table': 'customer_service',
                'verbose_name': '\u5ba2\u670d\u4fe1\u606f',
                'verbose_name_plural': '\u5ba2\u670d\u4fe1\u606f',
            },
        ),
        migrations.AlterModelOptions(
            name='config',
            options={'verbose_name': '\u914d\u7f6e\u6587\u4ef6', 'verbose_name_plural': '\u914d\u7f6e\u6587\u4ef6'},
        ),
    ]
