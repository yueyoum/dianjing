# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0002_auto_20150918_1359'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='character',
            options={'ordering': ('-last_login',)},
        ),
    ]
