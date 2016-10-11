# -*- coding: utf-8 -*-
import arrow

from django.db import models
from django.db import connection


class MailHistoryRecord(models.Model):
    id = models.UUIDField(primary_key=True)
    from_id = models.IntegerField(db_index=True, verbose_name="发送者")
    to_id = models.IntegerField(db_index=True, verbose_name="接收者")
    title = models.CharField(max_length=255, verbose_name="标题")
    content = models.TextField(verbose_name="内容")
    has_read = models.BooleanField(default=False, verbose_name="已读")
    attachment = models.TextField(default="", blank=True, verbose_name="附件")
    function = models.IntegerField(default=0, verbose_name="功能")

    create_at = models.DateTimeField(db_index=True, verbose_name="创建时间")

    def save(self, *args, **kwargs):
        self.title = self.title[:255]
        super(MailHistoryRecord, self).save(*args, **kwargs)

    class Meta:
        db_table = 'mail_history_record'
        ordering = ['-create_at', ]
        verbose_name = '邮件历史记录'
        verbose_name_plural = '邮件历史记录'

    @classmethod
    def create(cls, _id, from_id, to_id, title, content, attachment, function, create_at):
        cls.objects.create(
            id=_id,
            from_id=from_id,
            to_id=to_id,
            title=title,
            content=content,
            has_read=False,
            attachment=attachment,
            function=function,
            create_at=create_at
        )

    @classmethod
    def set_read(cls, _id):
        cls.objects.filter(id=_id).update(has_read=True)

    @classmethod
    def cronjob(cls):
        connection.close()

        limit = arrow.utcnow().replace(days=-15).format("YYYY-MM-DD HH:mm:ssZ")
        cls.objects.filter(create_at__lte=limit).delete()
