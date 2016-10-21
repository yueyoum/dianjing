# -*- coding: utf-8 -*-

import os
import uuid
import arrow

from django.db import models
from django.db.models import Q
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.utils import ProgrammingError
from django.core.validators import validate_comma_separated_integer_list

from apps.server.models import Server
from apps.character.models import Character


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


class Mail(models.Model):
    CONDITION_TYPE = (
        (1, '全部服务器'),
        (2, '指定服务器'),
        (3, '排除指定服务器'),

        (11, '指定角色ID'),
    )

    STATUS = (
        (0, '等待'),
        (1, '正在发送'),
        (2, '完成'),
        (3, '失败'),
    )

    title = models.CharField(max_length=255, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    items = models.TextField(blank=True, verbose_name='附件')

    send_at = models.DateTimeField(db_index=True, verbose_name='发送时间')

    condition_type = models.IntegerField(choices=CONDITION_TYPE, verbose_name='发送条件')
    condition_value = models.CharField(max_length=255, blank=True, null=True,
                                       validators=[validate_comma_separated_integer_list], verbose_name='条件值ID列表')

    condition_club_level = models.PositiveIntegerField(blank=True, null=True, verbose_name='俱乐部等级大于等于')
    condition_vip_level = models.PositiveIntegerField(blank=True, null=True, verbose_name='VIP等级大于等于')
    condition_login_at_1 = models.DateTimeField(blank=True, null=True, verbose_name='登陆时间大于等于')
    condition_login_at_2 = models.DateTimeField(blank=True, null=True, verbose_name='登陆时间小于等于')
    condition_exclude_chars = models.CharField(max_length=255, blank=True, null=True,
                                               validators=[validate_comma_separated_integer_list], verbose_name='排除角色ID列表')

    create_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    status = models.IntegerField(choices=STATUS, default=0, db_index=True, verbose_name='状态')

    def __unicode__(self):
        return self.title

    def has_condition(self):
        return self.condition_club_level is not None or self.condition_vip_level is not None or \
                self.condition_login_at_1 is not None or self.condition_login_at_2 is not None or \
                self.condition_exclude_chars is not None

    def get_parsed_condition_value(self):
        if not self.condition_value:
            return []
        return [int(_i) for _i in self.condition_value.split(',')]

    def get_parsed_condition_exclude_chars(self):
        if not self.condition_exclude_chars:
            return []
        return [int(_i) for _i in self.condition_exclude_chars.split(',')]

    def clean(self):
        def clean_condition():
            if (self.condition_login_at_1 and not self.condition_login_at_2) or \
                    (not self.condition_login_at_1 and self.condition_login_at_2):
                raise ValidationError("登陆时间范围需要同时设置")

            if self.condition_login_at_1:
                if self.condition_login_at_2 <= self.condition_login_at_1:
                    raise ValidationError("登陆时间范围第二个值必须大于第一个值")

            for i in self.get_parsed_condition_exclude_chars():
                if not Character.objects.filter(id=i).exists():
                    raise ValidationError("角色ID {0} 不存在".format(i))

        if self.condition_type == 1:
            if self.condition_value:
                raise ValidationError("全部服务器不用填写 条件值")

            clean_condition()

        elif self.condition_type in [2, 3]:
            for i in self.get_parsed_condition_value():
                if not Server.objects.filter(id=i).exists():
                    raise ValidationError("服务器 {0} 不存在".format(i))

            clean_condition()

        else:
            if self.has_condition():
                raise ValidationError("指定角色时 不用填写条件")

            for i in self.get_parsed_condition_value():
                if not Character.objects.filter(id=i).exists():
                    raise ValidationError("角色ID {0} 不存在".format(i))

    class Meta:
        db_table = 'mail'
        verbose_name = '邮件'
        verbose_name_plural = '邮件'
