# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0003_auto_20150506_1550'),
    ]

    operations = [
        migrations.RunSQL(
            "alter table staff_training modify id bigint(20) not null",
            "alter table staff_training modify id int(11) not null",
        )
    ]
