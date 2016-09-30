# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       urls
Date Created:   2015-08-31 14:53
Description:

"""

from django.conf.urls import url

import views_api.session
import views_api.union
import views_api.party

urlpatterns = [
    url(r'^session/parse/$', views_api.session.parse_session),

    url(r'^union/info/$', views_api.union.get_info),

    url(r'^party/create/$', views_api.party.create),
    url(r'^party/start/$', views_api.party.start),
    url(r'^party/buy/$', views_api.party.buy),
    url(r'^party/end/$', views_api.party.end),
]
