# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.core.exceptions import ValidationError


class GiftCode(models.Model):
    id = models.CharField(max_length=255, primary_key=True, verbose_name='名字')
    items = models.TextField()

    mail_title = models.CharField(max_length=255, verbose_name='邮件标题')
    mail_content = models.TextField(verbose_name='邮件内容')

    times_limit = models.IntegerField(default=1, verbose_name='总使用次数限制',
                                      help_text='单个礼品码的总使用次数，包括不同玩家，不同服')
    active = models.BooleanField(default=True, verbose_name='是否激活')
    create_at = models.DateTimeField(auto_now_add=True)

    time_range1 = models.DateTimeField(blank=True, null=True, verbose_name='使用时间起始')
    time_range2 = models.DateTimeField(blank=True, null=True, verbose_name='使用时间结束')

    class Meta:
        db_table = 'gift_code'
        verbose_name = '礼包配置'
        verbose_name_plural = '礼包配置'

    def __unicode__(self):
        return self.id

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


class GiftCodeGen(models.Model):
    category = models.ForeignKey(GiftCode, verbose_name='礼包')
    amount = models.IntegerField(verbose_name='生成数量')
    used_amount = models.IntegerField(default=0, verbose_name='使用数量')

    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'gift_code_gen'
        ordering = ['-id']
        verbose_name = '礼品码生成'
        verbose_name_plural = '礼品码生成'

    def clean(self):
        if self.amount < 1:
            raise ValidationError("amount must >= 1")


class GiftCodeRecord(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    gen_id = models.IntegerField(db_index=True)
    category = models.CharField(max_length=255)

    class Meta:
        db_table = 'gift_code_record'


class GiftCodeUsingLog(models.Model):
    server_id = models.IntegerField()
    char_id = models.IntegerField(db_index=True)
    # gift_code 就是上面的 GiftCodeRecord.id
    gift_code = models.CharField(db_index=True, max_length=255)
    category = models.CharField(max_length=255, db_index=True)
    using_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'gift_code_using_log'
        verbose_name = '礼品码使用记录'
        verbose_name_plural = '礼品码使用记录'
