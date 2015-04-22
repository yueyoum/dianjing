# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Character',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('account_id', models.IntegerField()),
                ('server_id', models.IntegerField()),
                ('name', models.CharField(max_length=32, db_index=True)),
                ('create_at', models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
            options={
                'db_table': 'char_',
            },
        ),
        migrations.AlterUniqueTogether(
            name='character',
            unique_together=set([('server_id', 'name'), ('account_id', 'server_id')]),
        ),
    ]
