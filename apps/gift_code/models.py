# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.core.exceptions import ValidationError

class GiftCode(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    items = models.TextField()

    mail_title = models.CharField(max_length=255)
    mail_content = models.TextField()

    times_limit = models.IntegerField(default=1)
    active = models.BooleanField(default=True)
    create_at = models.DateTimeField(auto_now_add=True)

    time_range1 = models.DateTimeField(blank=True, null=True)
    time_range2 = models.DateTimeField(blank=True, null=True)


    class Meta:
        db_table = 'gift_code'
        verbose_name = '礼品码'
        verbose_name_plural = '礼品码'

    def get_parsed_items(self):
        items = []
        for item in self.items.split(';'):
            _id, _amount = item.split(',')
            _id = int(_id)
            _amount = int(_amount)
            items.append((_id, _amount))

        return items

    def clean(self):
        try:
            self.get_parsed_items()
        except:
            raise ValidationError("items error")


class GiftCodeUsingLog(models.Model):
    char_id = models.IntegerField(db_index=True)
    gift_code = models.CharField(db_index=True, max_length=255)
    using_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'gift_code_using_log'
        verbose_name = '礼品码使用记录'
        verbose_name_plural = '礼品码使用记录'