# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       urls
Date Created:   2015-08-31 14:45
Description:

"""

from django.conf.urls import url

urlpatterns = [
    url(r'^search-index/$', 'background.views.data'),
    url(r'^server/$', 'background.views.servers'),
    url(r'^char/$', 'background.views.char'),
    url(r'^char/staff/$', 'background.views.staff'),
    url(r'^char/friend/$', 'background.views.friend'),
    url(r'^ladder/$', 'background.views.ladder'),
    url(r'^cup/$', 'background.views.cup'),
]
