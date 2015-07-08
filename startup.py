# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       startup
Date Created:   2015-04-23 23:30
Description:

"""

def setup():
    from core.db import mongo_connect
    mongo_connect()

    from config import load_config
    load_config()

    import signals
    import cronjob

