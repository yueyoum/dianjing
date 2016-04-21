# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       app
Date Created:   2015-08-19 16:16
Description:

"""

import os
from django.apps import AppConfig
from django.conf import settings


class ProjectConfig(AppConfig):
    name = 'apps.helper'

    def ready(self):
        from core.db import RedisDB
        RedisDB.get().ping()

        from core.mongo import ensure_index
        ensure_index()

        from config import load_config
        load_config()

        import signals
        import formula

        if not settings.TEST:
            from utils.api import Timerd
            Timerd.ping()

        if os.environ.get('UWSGI_RUNNING', '0') == '1':
            import cronjob
