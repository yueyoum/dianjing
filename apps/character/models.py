# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError
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


class ForbidChat(models.Model):
    char_id = models.IntegerField(db_index=True)
    reason = models.TextField(blank=True)

    unforbidden_at = models.DateTimeField(db_index=True, verbose_name="解除时间")
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'forbid_chat'
        ordering = ('-id', )
        verbose_name = "禁止聊天"
        verbose_name_plural = "禁止聊天"

    def clean(self):
        if not Character.objects.filter(id=self.char_id).exists():
            raise ValidationError("char_id {0} not exists".format(self.char_id))
