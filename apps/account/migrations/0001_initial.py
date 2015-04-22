# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tp', models.CharField(max_length=32, db_index=True)),
                ('register_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('last_login', models.DateTimeField(auto_now=True, db_index=True)),
                ('last_server_id', models.IntegerField(default=0)),
                ('login_times', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'account',
            },
        ),
        migrations.CreateModel(
            name='AccountRegular',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('passwd', models.CharField(max_length=255)),
                ('account', models.OneToOneField(related_name='info_regular', to='account.Account')),
            ],
            options={
                'db_table': 'account_regular',
            },
        ),
        migrations.CreateModel(
            name='AccountThird',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('platform', models.CharField(max_length=255)),
                ('uid', models.CharField(max_length=255)),
                ('account', models.OneToOneField(related_name='info_third', to='account.Account')),
            ],
            options={
                'db_table': 'account_third',
            },
        ),
        migrations.AlterUniqueTogether(
            name='accountthird',
            unique_together=set([('platform', 'uid')]),
        ),
    ]
