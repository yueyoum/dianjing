# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       game
Date Created:   2016-03-30 10-17
Description:

"""
from django.core.management.base import BaseCommand

from apps.server.models import Server
from apps.account.models import Account, AccountBan, AccountLoginLog, AccountRegular, AccountThird
from apps.character.models import Character
from apps.statistics.models import Statistics
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
        else:
            self.stderr.write("unknown command!")

    def _reset(self):
        RedisDB.connect()
        MongoDB.connect()

        Statistics.objects.all().delete()
        Character.objects.all().delete()
        AccountBan.objects.all().delete()
        AccountLoginLog.objects.all().delete()
        AccountThird.objects.all().delete()
        AccountRegular.objects.all().delete()
        Account.objects.all().delete()


        RedisDB.get().flushall()

        # TODO fix this
        db_names = []
        for s in Server.objects.all():
            db_names.append(s.mongo_db)
            db_names.append(s.mongo_db + "test")

        for mc in MongoDB.INSTANCES.values():
            for name in db_names:
                mc.drop_database(name)
