# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import utils.dbfields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LeagueBattle',
            fields=[
                ('id', utils.dbfields.BigAutoField(serialize=False, primary_key=True)),
                ('league_group', models.BigIntegerField(db_index=True)),
                ('league_order', models.IntegerField(db_index=True)),
            ],
            options={
                'db_table': 'league_battle',
                'verbose_name': 'League Battle',
                'verbose_name_plural': 'League Battle',
            },
        ),
        migrations.CreateModel(
            name='LeagueClubInfo',
            fields=[
                ('id', utils.dbfields.BigAutoField(serialize=False, primary_key=True)),
                ('club_id', models.IntegerField(db_index=True)),
                ('group_id', models.BigIntegerField(db_index=True)),
                ('battle_times', models.IntegerField(default=0)),
                ('win_times', models.IntegerField(default=0)),
                ('score', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'league_club_info',
                'verbose_name': 'Club Info',
                'verbose_name_plural': 'Club Info',
            },
        ),
        migrations.CreateModel(
            name='LeagueGame',
            fields=[
                ('id', utils.dbfields.BigAutoField(serialize=False, primary_key=True)),
                ('current_order', models.IntegerField(default=1)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ('-id',),
                'db_table': 'league_game',
                'verbose_name': 'League Game',
                'verbose_name_plural': 'League Game',
            },
        ),
        migrations.CreateModel(
            name='LeagueGroup',
            fields=[
                ('id', utils.dbfields.BigAutoField(serialize=False, primary_key=True)),
                ('server_id', models.IntegerField(db_index=True)),
                ('level', models.IntegerField()),
            ],
            options={
                'db_table': 'league_group',
                'verbose_name': 'League Group',
                'verbose_name_plural': 'League Group',
            },
        ),
        migrations.CreateModel(
            name='LeagueNPCInfo',
            fields=[
                ('id', utils.dbfields.BigAutoField(serialize=False, primary_key=True)),
                ('group_id', models.BigIntegerField(db_index=True)),
                ('club_name', models.CharField(max_length=255)),
                ('manager_name', models.CharField(max_length=255)),
                ('staffs_info', models.TextField()),
                ('battle_times', models.IntegerField(default=0)),
                ('win_times', models.IntegerField(default=0)),
                ('score', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'league_npc_info',
                'verbose_name': 'NPC Info',
                'verbose_name_plural': 'NPC Info',
            },
        ),
        migrations.CreateModel(
            name='LeaguePair',
            fields=[
                ('id', utils.dbfields.BigAutoField(serialize=False, primary_key=True)),
                ('league_battle', models.BigIntegerField(db_index=True)),
                ('club_one', models.BigIntegerField(default=0)),
                ('club_two', models.BigIntegerField(default=0)),
                ('npc_one', models.BigIntegerField(default=0)),
                ('npc_two', models.BigIntegerField(default=0)),
                ('win_one', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'league_pair',
                'verbose_name': 'League Pair',
                'verbose_name_plural': 'League Pair',
            },
        ),
    ]
