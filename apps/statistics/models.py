# -*- coding: utf-8 -*-

import uuid
from django.db import models

class Statistics(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    create_at = models.DateTimeField(auto_now_add=True, db_index=True)

    server_id = models.IntegerField()
    char_id = models.IntegerField(db_index=True)

    club_gold = models.IntegerField(default=0, verbose_name='金币')
    club_diamond = models.IntegerField(default=0, verbose_name='钻石')

    message = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'statistics'
        verbose_name = '统计'
        verbose_name_plural = '统计'
