# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-02-04 15:24
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gift_code', '0003_auto_20170204_2258'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='giftcoderecord',
            name='category',
        ),
    ]