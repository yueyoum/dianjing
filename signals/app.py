# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       config
Date Created:   2015-09-02 13:48
Description:

"""

import arrow

from django.conf import settings

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from apps.config.models import Config
from apps.server.models import Server
from apps.character.models import Character, ForbidChat

from core.mongo import ensure_index
from core.chat import Chat


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
def server_save(instance, created, **kwargs):
    if created:
        ensure_index(instance.id)


@receiver(post_save, sender=ForbidChat, dispatch_uid='ForbidChat.post_save')
def chat_forbidden_change(instance, **kwargs):
    expire_at = arrow.get(instance.unforbidden_at).to(settings.TIME_ZONE).replace(seconds=-1)

    char_id = instance.char_id
    server_id = Character.objects.get(id=char_id).server_id

    Chat(server_id, char_id).set_forbidden(expire_at)


@receiver(post_delete, sender=ForbidChat, dispatch_uid='ForbidChat.post_delete')
def chat_forbidden_delete(instance, **kwargs):
    char_id = instance.char_id
    server_id = Character.objects.get(id=char_id).server_id
    Chat(server_id, char_id).remove_forbidden()
