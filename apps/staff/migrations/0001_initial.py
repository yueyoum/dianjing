# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('char_id', models.IntegerField()),
                ('oid', models.IntegerField()),
                ('level', models.IntegerField(default=1)),
                ('exp', models.IntegerField(default=0)),
                ('status', models.IntegerField(default=3)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('property_add', models.CharField(default=b'{"fs": 0, "bb": 0, "qz": 0, "yy": 0, "cz": 0, "ys": 0, "jg": 0, "xt": 0}', max_length=255)),
                ('skills', models.CharField(default=b'{}', max_length=255)),
            ],
            options={
                'db_table': 'staff',
            },
        ),
        migrations.CreateModel(
            name='StaffTraining',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('staff_id', models.IntegerField()),
                ('training_id', models.IntegerField()),
                ('start_at', models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
            options={
                'ordering': ('id',),
                'db_table': 'staff_training',
            },
        ),
        migrations.AlterIndexTogether(
            name='stafftraining',
            index_together=set([('staff_id', 'training_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='staff',
            unique_together=set([('char_id', 'oid')]),
        ),
    ]
