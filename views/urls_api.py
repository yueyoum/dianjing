# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       urls
Date Created:   2015-08-31 14:53
Description:

"""

from django.conf.urls import url

urlpatterns = [
    url(r'^timerd/building/$', 'views.api.timerd.building_levelup_callback'),
]
