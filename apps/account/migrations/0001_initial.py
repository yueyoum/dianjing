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
                ('login_times', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'account',
            },
        ),
        migrations.CreateModel(
            name='AccountBan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('account_id', models.IntegerField(verbose_name=b'\xe5\xb8\x90\xe5\x8f\xb7ID')),
                ('ban', models.BooleanField(verbose_name=b'\xe6\x98\xaf\xe5\x90\xa6\xe5\x86\xbb\xe7\xbb\x93')),
                ('ban_at', models.DateTimeField(auto_now_add=True, verbose_name=b'\xe5\x86\xbb\xe7\xbb\x93\xe5\xbc\x80\xe5\xa7\x8b\xe6\x97\xb6\xe9\x97\xb4')),
                ('unban_at', models.DateTimeField(verbose_name=b'\xe5\x86\xbb\xe7\xbb\x93\xe7\xbb\x93\xe6\x9d\x9f\xe6\x97\xb6\xe9\x97\xb4', db_index=True)),
                ('reason', models.TextField(verbose_name=b'\xe5\x8e\x9f\xe5\x9b\xa0', blank=True)),
            ],
            options={
                'db_table': 'account_ban',
                'verbose_name': '\u5e10\u53f7\u51bb\u7ed3',
                'verbose_name_plural': '\u8d26\u53f7\u51bb\u7ed3',
            },
        ),
        migrations.CreateModel(
            name='AccountLoginLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('account_id', models.IntegerField(verbose_name=b'\xe5\xb8\x90\xe5\x8f\xb7ID', db_index=True)),
                ('login_at', models.DateTimeField(auto_now_add=True, verbose_name=b'\xe7\x99\xbb\xe5\xbd\x95\xe6\x97\xb6\xe9\x97\xb4', db_index=True)),
                ('ip', models.CharField(max_length=32, verbose_name=b'\xe7\x99\xbb\xe5\xbd\x95IP')),
                ('to_server_id', models.IntegerField(verbose_name=b'\xe5\x8c\xbaID')),
            ],
            options={
                'db_table': 'account_login_log',
                'verbose_name': '\u767b\u5f55\u65e5\u5fd7',
                'verbose_name_plural': '\u767b\u5f55\u65e5\u5fd7',
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
            name='accountban',
            unique_together=set([('account_id', 'ban')]),
        ),
        migrations.AlterUniqueTogether(
            name='accountthird',
            unique_together=set([('platform', 'uid')]),
        ),
    ]
