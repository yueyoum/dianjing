# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       urls
Date Created:   2015-08-31 14:45
Description:

"""

from django.conf.urls import url

urlpatterns = [
    url(r'^$', 'background.views.servers'),
    url(r'^collections/$', 'background.views.collections'),
    url(r'^building/$', 'background.views.building'),
    url(r'^character/$', 'background.views.character'),
    url(r'^character/club/$', 'background.views.club'),
    url(r'^friend/$', 'background.views.friend'),
    url(r'^mail/$', 'background.views.mail'),
    url(r'^mail/one/$', 'background.views.mail_one'),
    url(r'^staff/$', 'background.views.staff'),
    url(r'^staff/char/$', 'background.views.staff_char'),
    url(r'^recruit/$', 'background.views.recruit'),
    url(r'^league_event/$', 'background.views.league_event'),
    url(r'^league_group/$', 'background.views.league_group'),
    url(r'^training_store/$', 'background.views.training_store'),
]
