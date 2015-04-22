# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Club',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('char_id', models.IntegerField(db_index=True)),
                ('char_name', models.CharField(max_length=32)),
                ('server_id', models.IntegerField()),
                ('name', models.CharField(max_length=32)),
                ('flag', models.IntegerField()),
                ('level', models.IntegerField(default=1)),
                ('renown', models.IntegerField(default=0)),
                ('vip', models.IntegerField(default=0)),
                ('exp', models.IntegerField(default=0)),
                ('gold', models.IntegerField(default=0)),
                ('sycee', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'club',
            },
        ),
        migrations.AlterUniqueTogether(
            name='club',
            unique_together=set([('name', 'server_id')]),
        ),
    ]
