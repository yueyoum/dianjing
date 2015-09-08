# -*- coding: utf-8 -*-

import arrow

from django.db import models
from django.db import connection

class Server(models.Model):
    STATUS = (
        (1, "新"),
        (2, "火"),
    )

    id = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=32)
    status = models.IntegerField(choices=STATUS, default=1)

    open_at = models.DateTimeField(db_index=True)

    mongo_host = models.CharField(max_length=16)
    mongo_port = models.IntegerField()
    mongo_db = models.CharField(max_length=16)

    class Meta:
        db_table = 'server'

    @classmethod
    def opened_servers(cls):
        connection.close()

        now = arrow.utcnow().format("YYYY-MM-DD HH:mm:ssZ")
        servers = cls.objects.filter(open_at__lte=now)
        return servers
