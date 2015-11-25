# -*- coding: utf-8 -*-

from django.db import models

class Character(models.Model):
    account_id = models.IntegerField()
    server_id = models.IntegerField()
    name = models.CharField(max_length=32, db_index=True)
    create_at = models.DateTimeField(auto_now_add=True, db_index=True)
    club_name = models.CharField(max_length=32, null=True)

    last_login = models.DateTimeField(auto_now=True, db_index=True)
    login_times = models.BigIntegerField(default=0)

    avatar_key = models.CharField(max_length=255, verbose_name="头像key")
    avatar_ok = models.BooleanField(default=False, verbose_name="头像审核通过")

    class Meta:
        db_table = 'char_'
        ordering = ('-last_login',)
        unique_together = (
            ('account_id', 'server_id'),
            ('server_id', 'name'),
            ('club_name', 'server_id')
        )

        verbose_name = "角色"
        verbose_name_plural = "角色"
