# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       config
Date Created:   2015-09-02 13:48
Description:

"""


from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from apps.config.models import Config
from apps.server.models import Server

from core.mongo import ensure_index


def config_change(**kwargs):
    import uwsgi
    uwsgi.reload()


post_save.connect(
    config_change,
    sender=Config,
    dispatch_uid='Config.post_save'
)

post_delete.connect(
    config_change,
    sender=Config,
    dispatch_uid='Config.post_delete'
)

@receiver(post_save, sender=Server, dispatch_uid='Server.post_save')
def server_save(instance, **kwargs):
    ensure_index(instance.id)

