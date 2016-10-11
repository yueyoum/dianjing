# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       mongodb
Date Created:   2015-09-11 14:36
Description:

"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "create index in mongodb"

    def add_arguments(self, parser):
        parser.add_argument(
            'cmd',
            # nargs='+',
            type=str
        )

    def handle(self, *args, **options):
        if options['cmd'] == 'createindex':
            self._create_index()
        else:
            self.stderr.write("unknown command!")

    def _create_index(self):
        from core.mongo import ensure_index
        from apps.server.models import Server
        for s in Server.objects.all():
            ensure_index(s.id)
