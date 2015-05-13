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
                ('club_one', models.IntegerField(default=0)),
                ('club_two', models.IntegerField(default=0)),
                ('npc_one', models.BigIntegerField(default=0)),
                ('npc_two', models.BigIntegerField(default=0)),
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
                ('group_id', models.BigIntegerField()),
                ('battle_times', models.IntegerField()),
                ('score', models.IntegerField()),
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
                ('club_name', models.CharField(max_length=255)),
                ('manager_name', models.CharField(max_length=255)),
                ('npc_id', models.IntegerField()),
                ('staffs_info', models.TextField()),
            ],
            options={
                'db_table': 'league_npc_info',
                'verbose_name': 'NPC Info',
                'verbose_name_plural': 'NPC Info',
            },
        ),
    ]
