# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       gift_code
Date Created:   2017-02-04 21:40
Description:

"""


from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.gift_code.models import GiftCodeGen, GiftCodeRecord

from utils.functional import make_signed_random_string


@receiver(post_save, sender=GiftCodeGen, dispatch_uid='GiftCodeGen.post_save')
def generate_gift_code(instance, **kwargs):
    if GiftCodeRecord.objects.filter(gen_id=instance.id).exists():
        return

    gen_id = instance.id
    category = instance.category.id

    code_text_sets = set()
    data = []

    while len(data) < instance.amount:
        code_text = make_signed_random_string()
        if code_text in code_text_sets:
            continue

        code_text_sets.add(code_text)

        obj = GiftCodeRecord(
            id=code_text,
            gen_id=gen_id,
            category=category,
        )

        data.append(obj)

    GiftCodeRecord.objects.bulk_create(data)

