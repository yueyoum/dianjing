# -*- coding: utf-8 -*-

from django.db import models

# 其实就是club
class Character(models.Model):
    account_id = models.IntegerField()
    server_id = models.IntegerField()
    # 这个name 以前是 角色名，现在就当做 club_name 了
    name = models.CharField(max_length=32, db_index=True)
    create_at = models.DateTimeField(auto_now_add=True, db_index=True)

    last_login = models.DateTimeField(auto_now=True, db_index=True)
    login_times = models.BigIntegerField(default=0)

    class Meta:
        db_table = 'char_'
        ordering = ('-last_login',)
        unique_together = (
            ('account_id', 'server_id'),
            ('server_id', 'name'),
        )

        verbose_name = "角色(俱乐部)"
        verbose_name_plural = "角色(俱乐部)"
