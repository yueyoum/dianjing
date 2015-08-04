# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       startup
Date Created:   2015-04-23 23:30
Description:

"""

from django.conf import settings

def setup():
    from core.db import connect
    connect()

    from config import load_config
    load_config()

    import signals

    if not settings.TEST:
        import cronjob

