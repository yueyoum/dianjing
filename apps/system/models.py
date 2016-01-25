# -*- coding:utf-8 -*-

import os
import uuid

from django.db import models
from django.conf import settings

def upload_to(instance, filename):
    _, ext = os.path.splitext(filename)
    name = "{0}{1}".format(str(uuid.uuid4()), ext)
    return os.path.join(settings.UPLOAD_DIR, name)


class Bulletin(models.Model):
    title = models.CharField(max_length=255, verbose_name="标题")
    content = models.TextField(verbose_name="内容", blank=True)
    image = models.FileField(verbose_name="图片", null=True, blank=True, upload_to=upload_to)

    order_num = models.IntegerField(default=1, db_index=True, verbose_name="排列序号",
                                    help_text="数字越大越靠前"
                                    )

    display = models.BooleanField(default=True, db_index=True, verbose_name="是否显示")


    class Meta:
        db_table = 'bulletin'
        verbose_name = "公告"
        verbose_name_plural = "公告"

    def __unicode__(self):
        return self.title


class Broadcast(models.Model):
    content = models.CharField(max_length=255, verbose_name="内容")
    repeat_times = models.IntegerField(default=0, verbose_name="重复次数",
                                         help_text='0表示一直重复'
                                         )

    display = models.BooleanField(default=True, db_index=True, verbose_name="显示")

    class Meta:
        db_table = 'broadcast'
        verbose_name = "走马灯"
        verbose_name_plural = "走马灯"
