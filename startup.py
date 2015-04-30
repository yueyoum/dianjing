# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       startup
Date Created:   2015-04-23 23:30
Description:

"""


def start():
    from core.db import redis_client
    redis_client.ping()

    import signals
    from config import _load_config

    _load_config()
