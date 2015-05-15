# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0005_auto_20150515_1317'),
    ]

    operations = [
        migrations.RenameField(
            model_name='staff',
            old_name='char_id',
            new_name='club_id',
        ),

        migrations.AlterUniqueTogether(
            name='staff',
            unique_together=set([('club_id', 'oid')]),
        ),
    ]
