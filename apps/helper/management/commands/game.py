# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       game
Date Created:   2016-03-30 10-17
Description:

"""
from django.core.management.base import BaseCommand

from apps.server.models import Server
from apps.account.models import (
    Account,
    AccountBan,
    AccountLoginLog,
    AccountRegular,
    AccountThird,
    GeTuiClientID,
)

from apps.character.models import Character
from apps.statistics.models import Statistics
from apps.history_record.models import MailHistoryRecord
from apps.config.models import CustomerServiceInformation
from apps.gift_code.models import GiftCodeUsingLog

from core.db import MongoDB, RedisDB
from core.mongo import ensure_index


class Command(BaseCommand):
    help = """Game Management
    commands:
    reset - clear records. (mysql, mongodb, redis)
    """

    def add_arguments(self, parser):
        parser.add_argument(
            'cmd',
            # nargs='+',
            type=str
        )

    def handle(self, *args, **options):
        if options['cmd'] == 'reset':
            self._reset()
        elif options['cmd'] == 'empty_cache':
            self._empty_cache()
        elif options['cmd'] == 'initmodel':
            self._init_model()
        else:
            self.stderr.write("unknown command!")

    def _reset(self):
        RedisDB.connect()
        MongoDB.connect()

        GiftCodeUsingLog.objects.all().delete()
        # GiftCodeRecord.objects.all().delete()
        # GiftCodeGen.objects.all().delete()
        # GiftCode.objects.all().delete()

        MailHistoryRecord.objects.all().delete()
        Statistics.objects.all().delete()
        Character.objects.all().delete()
        AccountBan.objects.all().delete()
        AccountLoginLog.objects.all().delete()
        AccountThird.objects.all().delete()
        AccountRegular.objects.all().delete()
        Account.objects.all().delete()
        GeTuiClientID.objects.all().delete()

        RedisDB.get().flushdb()
        RedisDB.get(1).flushdb()

        for mc in MongoDB.DBS.values():
            mc.client.drop_database(mc.name)

        for s in Server.objects.all():
            ensure_index(s.id)

    def _empty_cache(self):
        RedisDB.connect()
        RedisDB.get().flushall()

    def _init_model(self):
        name_values = {
            'qq': '123456',
            'qq_group': '123456',
            'email': 'a@b.c',
            '1sdk_callback': 'DOMAIN/callback/1sdk/',
            # 'stars_cloud_callback': 'DOMAIN/callback/stars_cloud/',
        }

        for n, v in name_values.iteritems():
            if not CustomerServiceInformation.objects.filter(name=n).exists():
                CustomerServiceInformation.objects.create(
                    name=n,
                    value=v,
                )
