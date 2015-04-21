# -*- coding: utf-8 -*-

from django.db import models

class Server(models.Model):
    STATUS = (
        (1, "新"),
        (2, "火"),
    )

    id = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=32)
    status = models.IntegerField(choices=STATUS, default=1)

    open_at = models.DateTimeField(db_index=True)

    class Meta:
        db_table = 'server'

