# -*- coding: utf-8 -*-

import arrow

from django.conf import settings
from django.db import models
from django.db import connection


class Server(models.Model):
    STATUS = (
        (1, "正常"),
        (2, "火爆"),
        (3, "维护"),
    )

    id = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=32)
    status = models.IntegerField(choices=STATUS, default=1)
    is_new = models.BooleanField(default=False)

    open_at = models.DateTimeField(db_index=True)

    class Meta:
        db_table = 'server'

    @classmethod
    def opened_servers(cls):
        connection.close()

        now = arrow.utcnow().format("YYYY-MM-DD HH:mm:ssZ")
        servers = cls.objects.filter(open_at__lte=now)
        return servers

    @classmethod
    def duty_server_ids(cls):
        ids = []
        for s in cls.opened_servers():
            if settings.DUTY_SERVER_MIN <= s.id <= settings.DUTY_SERVER_MAX:
                ids.append(s.id)

        return ids
