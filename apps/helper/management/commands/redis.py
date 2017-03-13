# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       redis
Date Created:   2017-03-13 16:56
Description:

"""
import arrow

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.character.models import Character, ForbidChat
from core.chat import Chat

class Command(BaseCommand):
    help = "redis"

    def add_arguments(self, parser):
        parser.add_argument(
            'cmd',
            # nargs='+',
            type=str
        )

    def handle(self, *args, **options):
        if options['cmd'] == 'sync_from_db':
            self._sync_from_db()
        else:
            self.stderr.write("unknown command!")

    def _sync_from_db(self):
        now = arrow.utcnow().format("YYYY-MM-DD HH:mm:ssZ")
        for obj in ForbidChat.objects.filter(unforbidden_at__gt=now):
            expire_at = arrow.get(obj.unforbidden_at).to(settings.TIME_ZONE).replace(seconds=-1).timestamp
            char_id = obj.char_id
            server_id = Character.objects.get(id=char_id).server_id

            Chat(server_id, char_id).set_forbidden(expire_at)
