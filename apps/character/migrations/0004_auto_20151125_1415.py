# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0003_auto_20150918_1439'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='character',
            options={'ordering': ('-last_login',), 'verbose_name': '\u89d2\u8272', 'verbose_name_plural': '\u89d2\u8272'},
        ),
        migrations.AddField(
            model_name='character',
            name='avatar_key',
            field=models.CharField(default='', max_length=255, verbose_name=b'\xe5\xa4\xb4\xe5\x83\x8fkey'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='character',
            name='avatar_ok',
            field=models.BooleanField(default=False, verbose_name=b'\xe5\xa4\xb4\xe5\x83\x8f\xe5\xae\xa1\xe6\xa0\xb8\xe9\x80\x9a\xe8\xbf\x87'),
        ),
    ]
