# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       urls
Date Created:   2015-08-31 14:53
Description:

"""

from django.conf.urls import url

import views.api.session
import views.api.party

urlpatterns = [
    url(r'^session/parse/$', views.api.session.parse_session),
    url(r'^party/create/$', views.api.party.create),
    url(r'^party/start/$', views.api.party.start),
    url(r'^party/buy/$', views.api.party.buy),
    url(r'^party/end/$', views.api.party.end),
]
