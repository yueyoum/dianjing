# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       game
Date Created:   2016-03-30 10-17
Description:

"""
from django.core.management.base import BaseCommand

from apps.account.models import Account, AccountBan, AccountLoginLog, AccountRegular, AccountThird
from apps.character.models import Character
from apps.statistics.models import Statistics
from apps.history_record.models import MailHistoryRecord
from core.db import MongoDB, RedisDB


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
        else:
            self.stderr.write("unknown command!")

    def _reset(self):
        RedisDB.connect()
        MongoDB.connect()

        MailHistoryRecord.objects.all().delete()
        Statistics.objects.all().delete()
        Character.objects.all().delete()
        AccountBan.objects.all().delete()
        AccountLoginLog.objects.all().delete()
        AccountThird.objects.all().delete()
        AccountRegular.objects.all().delete()
        Account.objects.all().delete()

        RedisDB.get().flushall()

        for mc in MongoDB.DBS.values():
            mc.client.drop_database(mc.name)

    def _empty_cache(self):
        RedisDB.connect()
        RedisDB.get().flushall()
