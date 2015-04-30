# -*- coding: utf-8 -*-

from django.db import models
from apps.staff.property import StaffProperty

class Staff(models.Model):
    id = models.IntegerField(primary_key=True)
    char_id = models.IntegerField()
    oid = models.IntegerField()

    level = models.IntegerField(default=1)
    exp = models.IntegerField(default=0)
    # status see editor. staff_status.json
    status = models.IntegerField(default=3)

    create_at = models.DateTimeField(auto_now_add=True)

    # 属性增强，直接用json存储为varchar
    property_add = models.CharField(max_length=255, default=StaffProperty.DEFAULT_PROPERTY_ADD)
    # 技能，同样
    skills = models.CharField(max_length=255, default='{}')

    class Meta:
        db_table = 'staff'
        unique_together = (
            ('char_id', 'oid'),
        )


class StaffTraining(models.Model):
    id = models.IntegerField(primary_key=True)
    staff_id = models.IntegerField()
    training_id = models.IntegerField()

    start_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'staff_training'
        index_together = (
            ('staff_id', 'training_id'),
        )
        ordering = ('id',)
