# -*- coding: utf-8 -*-

import os
import uuid
import arrow

from django.db import models
from django.db.models import Q
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.utils import ProgrammingError

def config_upload_to(instance, filename):
    now = arrow.utcnow().to(settings.TIME_ZONE).format("YYYY-MM-DD-HH-mm-ss")
    name = "config-{0}-{1}.zip".format(instance.version, now)
    return os.path.join(settings.UPLOAD_DIR, name)


class Config(models.Model):
    version = models.CharField(max_length=255, primary_key=True)
    config = models.FileField(upload_to=config_upload_to)
    des = models.TextField(blank=True)
    in_use = models.BooleanField(default=False, db_index=True)

    class Meta:
        db_table = 'config'
        verbose_name = '配置文件'
        verbose_name_plural = '配置文件'

    def __unicode__(self):
        return self.version


    def clean(self):
        condition = (~Q(version=self.version)) & Q(in_use=True)
        if not self.in_use:
            if Config.objects.filter(condition).count() == 0:
                raise ValidationError("No Config in use")

    def save(self, **kwargs):
        if self.in_use:
            Config.objects.filter(~Q(version=self.version)).update(in_use=False)

        super(Config, self).save(**kwargs)

    @classmethod
    def get_config(cls):
        try:
            return cls.objects.get(in_use=True)
        except (Config.DoesNotExist, ProgrammingError):
            return None

class CustomerServiceInformation(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    value = models.CharField(max_length=255)

    des = models.TextField(blank=True)

    class Meta:
        db_table = 'customer_service'
        verbose_name = '自定义信息'
        verbose_name_plural = '自定义信息'


def image_upload_to(instance, filename):
    _, ext = os.path.splitext(filename)
    name = "{0}{1}".format(str(uuid.uuid4()), ext)
    return os.path.join(settings.UPLOAD_DIR, name)


class Bulletin(models.Model):
    title = models.CharField(max_length=255, verbose_name="标题")
    content = models.TextField(verbose_name="内容", blank=True)
    image = models.FileField(verbose_name="图片", null=True, blank=True, upload_to=image_upload_to)

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
    server_min = models.IntegerField(default=0, db_index=True)
    server_max = models.IntegerField(default=0, db_index=True)
    content = models.CharField(max_length=255, verbose_name="内容")
    repeat_times = models.IntegerField(default=0, verbose_name="重复次数",
                                         help_text='0表示一直重复'
                                         )

    display = models.BooleanField(default=True, verbose_name="显示")

    class Meta:
        db_table = 'broadcast'
        verbose_name = "走马灯"
        verbose_name_plural = "走马灯"
