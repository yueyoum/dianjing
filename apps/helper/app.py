# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       app
Date Created:   2015-08-19 16:16
Description:

"""

import os
from django.conf import settings
from django.apps import AppConfig


class ProjectConfig(AppConfig):
    name = 'apps.helper'

    def ready(self):
        from config import load_config
        load_config()

        import signals

        if not (settings.DUTY_SERVER_MIN == 0 and settings.DUTY_SERVER_MAX == 0) and os.environ.get('UWSGI_RUNNING', '0') == '1':
            import cronjob
