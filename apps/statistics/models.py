# -*- coding: utf-8 -*-

import arrow

import uuid
from django.db import models
from django.db import connection


class Statistics(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    create_at = models.DateTimeField(auto_now_add=True, db_index=True)

    server_id = models.IntegerField()
    char_id = models.IntegerField(db_index=True)

    club_gold = models.IntegerField(default=0, verbose_name='金币')
    club_diamond = models.IntegerField(default=0, verbose_name='钻石')

    message = models.CharField(max_length=255, blank=True, db_index=True)

    class Meta:
        db_table = 'statistics'
        ordering = ['-create_at']
        verbose_name = '财务统计'
        verbose_name_plural = '财务统计'

    @classmethod
    def cronjob(cls):
        connection.close()

        limit = arrow.utcnow().replace(days=-30).format("YYYY-MM-DD HH:mm:ssZ")
        num, _ = cls.objects.filter(create_at__lte=limit).delete()
        return num
